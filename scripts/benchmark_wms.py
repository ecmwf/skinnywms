#!/usr/bin/env python3
"""Benchmark a WMS endpoint with concurrent GetMap requests while polling GetCapabilities.

This script:
1. Fetches GetCapabilities and auto-discovers a valid GetMap query.
2. Runs concurrent GetMap requests for a given duration.
3. In parallel, polls GetCapabilities asynchronously at a fixed interval.
4. Prints p50/p95/p99 latency, throughput and error rates for both request types.
"""

from __future__ import annotations

import argparse
import asyncio
import csv
import concurrent.futures
import json
import subprocess
import statistics
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple


@dataclass
class RequestSample:
    ok: bool
    status: int
    latency_ms: float
    size_bytes: int
    error: str = ""


@dataclass
class Scenario:
    base_url: str
    version: str
    getcapabilities_url: str
    getmap_url: str
    layer: str
    style: str
    startup_getcapabilities_ms: float
    startup_getcapabilities_ok: bool
    startup_getcapabilities_status: int


def _percentile(values: List[float], p: float) -> float:
    if not values:
        return 0.0
    if len(values) == 1:
        return values[0]
    rank = (len(values) - 1) * p
    lower = int(rank)
    upper = min(lower + 1, len(values) - 1)
    weight = rank - lower
    return values[lower] * (1.0 - weight) + values[upper] * weight


def _stats(samples: List[RequestSample], wall_seconds: float) -> Dict[str, float]:
    latencies = sorted([s.latency_ms for s in samples if s.ok])
    total = len(samples)
    ok = sum(1 for s in samples if s.ok)
    err = total - ok

    return {
        "requests": float(total),
        "ok": float(ok),
        "errors": float(err),
        "error_pct": (err / total * 100.0) if total else 0.0,
        "rps": (total / wall_seconds) if wall_seconds > 0 else 0.0,
        "mean_ms": statistics.mean(latencies) if latencies else 0.0,
        "p50_ms": _percentile(latencies, 0.50),
        "p95_ms": _percentile(latencies, 0.95),
        "p99_ms": _percentile(latencies, 0.99),
    }


def _http_get(url: str, timeout: float) -> RequestSample:
    start = time.perf_counter()
    try:
        req = urllib.request.Request(url=url, method="GET")
        with urllib.request.urlopen(req, timeout=timeout) as response:
            body = response.read()
            status = int(response.status)
            ok = 200 <= status < 300
            elapsed_ms = (time.perf_counter() - start) * 1000.0
            return RequestSample(ok=ok, status=status, latency_ms=elapsed_ms, size_bytes=len(body))
    except Exception as exc:  # noqa: BLE001
        elapsed_ms = (time.perf_counter() - start) * 1000.0
        return RequestSample(ok=False, status=0, latency_ms=elapsed_ms, size_bytes=0, error=str(exc))


def _http_get_bytes(url: str, timeout: float) -> bytes:
    req = urllib.request.Request(url=url, method="GET")
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return response.read()


def _build_capabilities_url(base_url: str, version: str) -> str:
    params = {
        "service": "WMS",
        "request": "GetCapabilities",
        "version": version,
    }
    return f"{base_url}?{urllib.parse.urlencode(params)}"


def _build_root_url(base_url: str) -> str:
    parsed = urllib.parse.urlparse(base_url)
    root_path = "/"
    return urllib.parse.urlunparse((parsed.scheme, parsed.netloc, root_path, "", "", ""))


def _first_dimension_value(text: str) -> Optional[str]:
    if not text:
        return None
    value = text.strip()
    if not value:
        return None
    first = value.split(",", 1)[0].strip()
    if not first:
        return None
    if "/" in first:
        return first.split("/", 1)[0].strip() or None
    return first


def _extract_getmap_query(capabilities_xml: bytes, version: str, width: int, height: int, image_format: str) -> Tuple[Dict[str, str], str, str]:
    root = ET.fromstring(capabilities_xml)

    top_layer = root.find(".//{*}Capability/{*}Layer")

    global_boxes = []
    global_geo_bbox = None
    global_crss = []
    if top_layer is not None:
        for box in top_layer.findall("{*}BoundingBox"):
            box_crs = box.get("CRS") or box.get("SRS")
            minx = box.get("minx")
            miny = box.get("miny")
            maxx = box.get("maxx")
            maxy = box.get("maxy")
            if box_crs and None not in (minx, miny, maxx, maxy):
                global_boxes.append((box_crs, f"{minx},{miny},{maxx},{maxy}"))
        for crs_node in top_layer.findall("{*}CRS"):
            text = (crs_node.text or "").strip()
            if text:
                global_crss.append(text)
        geo = top_layer.find("{*}EX_GeographicBoundingBox")
        if geo is not None:
            west = (geo.findtext("{*}westBoundLongitude") or "-180").strip()
            south = (geo.findtext("{*}southBoundLatitude") or "-90").strip()
            east = (geo.findtext("{*}eastBoundLongitude") or "180").strip()
            north = (geo.findtext("{*}northBoundLatitude") or "90").strip()
            global_geo_bbox = ("CRS:84", f"{west},{south},{east},{north}")

    queryable_layers = []
    for layer in root.findall(".//{*}Layer"):
        if layer.get("queryable") == "1":
            name_el = layer.find("{*}Name")
            if name_el is not None and (name_el.text or "").strip():
                queryable_layers.append(layer)

    if not queryable_layers:
        for layer in root.findall(".//{*}Layer"):
            name_el = layer.find("{*}Name")
            if name_el is not None and (name_el.text or "").strip():
                queryable_layers.append(layer)

    if not queryable_layers:
        raise RuntimeError("No named layer found in GetCapabilities")

    layer = next(
        (
            entry
            for entry in queryable_layers
            if ((entry.findtext("{*}Name") or "").strip().lower() != "background")
        ),
        queryable_layers[0],
    )
    layer_name = layer.find("{*}Name").text.strip()

    style_el = layer.find("{*}Style/{*}Name")
    style_name = style_el.text.strip() if style_el is not None and (style_el.text or "").strip() else ""

    crs = None
    bbox = None

    preferred_boxes = []
    for box in layer.findall("{*}BoundingBox"):
        box_crs = box.get("CRS") or box.get("SRS")
        if not box_crs:
            continue
        try:
            minx = box.get("minx")
            miny = box.get("miny")
            maxx = box.get("maxx")
            maxy = box.get("maxy")
            if None in (minx, miny, maxx, maxy):
                continue
            coords = f"{minx},{miny},{maxx},{maxy}"
            preferred_boxes.append((box_crs, coords))
        except Exception:  # noqa: BLE001
            continue

    for preferred_crs in ("CRS:84", "EPSG:4326", "EPSG:3857"):
        hit = next((entry for entry in preferred_boxes if entry[0] == preferred_crs), None)
        if hit is not None:
            crs, bbox = hit
            break

    if crs is None and preferred_boxes:
        crs, bbox = preferred_boxes[0]

    if (crs is None or bbox is None) and global_boxes:
        for preferred_crs in ("CRS:84", "EPSG:4326", "EPSG:3857"):
            hit = next((entry for entry in global_boxes if entry[0] == preferred_crs), None)
            if hit is not None:
                crs, bbox = hit
                break

    if (crs is None or bbox is None) and global_boxes:
        crs, bbox = global_boxes[0]

    if (crs is None or bbox is None) and global_geo_bbox is not None:
        crs, bbox = global_geo_bbox

    if crs is None or bbox is None:
        geo = layer.find("{*}EX_GeographicBoundingBox")
        if geo is not None:
            west = (geo.findtext("{*}westBoundLongitude") or "-180").strip()
            south = (geo.findtext("{*}southBoundLatitude") or "-90").strip()
            east = (geo.findtext("{*}eastBoundLongitude") or "180").strip()
            north = (geo.findtext("{*}northBoundLatitude") or "90").strip()
            crs = "CRS:84"
            bbox = f"{west},{south},{east},{north}"

    if crs is None and global_crss:
        for preferred_crs in ("CRS:84", "EPSG:4326", "EPSG:3857"):
            if preferred_crs in global_crss:
                crs = preferred_crs
                break
        if crs is None:
            crs = global_crss[0]

    if bbox is None:
        bbox = "-180,-90,180,90"

    if crs is None or bbox is None:
        raise RuntimeError("Could not determine CRS/BBOX from GetCapabilities")

    params: Dict[str, str] = {
        "service": "WMS",
        "request": "GetMap",
        "version": version,
        "layers": layer_name,
        "styles": style_name,
        "format": image_format,
        "width": str(width),
        "height": str(height),
        "bbox": bbox,
        "transparent": "TRUE",
    }

    if version == "1.3.0":
        params["crs"] = crs
    else:
        params["srs"] = crs

    for dim in layer.findall("{*}Dimension"):
        dim_name = (dim.get("name") or "").strip().lower()
        if not dim_name:
            continue
        default = (dim.get("default") or "").strip()
        candidate = default or _first_dimension_value(dim.text or "")
        if candidate:
            params[dim_name] = candidate

    return params, layer_name, style_name


def discover_scenario(base_url: str, version: str, width: int, height: int, image_format: str, timeout: float) -> Scenario:
    getcapabilities_url = _build_capabilities_url(base_url, version)
    sample = _http_get(getcapabilities_url, timeout)
    if not sample.ok:
        raise RuntimeError(f"GetCapabilities failed: {sample.error or sample.status}")
    capabilities_xml = _http_get_bytes(getcapabilities_url, timeout)

    params, layer, style = _extract_getmap_query(
        capabilities_xml=capabilities_xml,
        version=version,
        width=width,
        height=height,
        image_format=image_format,
    )
    getmap_url = f"{base_url}?{urllib.parse.urlencode(params)}"
    return Scenario(
        base_url=base_url,
        version=version,
        getcapabilities_url=getcapabilities_url,
        getmap_url=getmap_url,
        layer=layer,
        style=style,
        startup_getcapabilities_ms=sample.latency_ms,
        startup_getcapabilities_ok=sample.ok,
        startup_getcapabilities_status=sample.status,
    )


def run_getmap_benchmark(url: str, duration_seconds: int, concurrency: int, timeout: float) -> Tuple[List[RequestSample], float]:
    samples: List[RequestSample] = []
    end_time = time.perf_counter() + duration_seconds

    def worker() -> List[RequestSample]:
        local: List[RequestSample] = []
        while time.perf_counter() < end_time:
            local.append(_http_get(url, timeout=timeout))
        return local

    start = time.perf_counter()
    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as pool:
        futures = [pool.submit(worker) for _ in range(concurrency)]
        for fut in concurrent.futures.as_completed(futures):
            samples.extend(fut.result())
    wall = time.perf_counter() - start
    return samples, wall


async def poll_getcapabilities(url: str, duration_seconds: int, interval_seconds: float, timeout: float) -> Tuple[List[RequestSample], float]:
    samples: List[RequestSample] = []
    start = time.perf_counter()
    end = start + duration_seconds

    while time.perf_counter() < end:
        sample = await asyncio.to_thread(_http_get, url, timeout)
        samples.append(sample)
        await asyncio.sleep(interval_seconds)

    wall = time.perf_counter() - start
    return samples, wall


def _print_report(title: str, stats: Dict[str, float]) -> None:
    print(f"\n{title}")
    print("-" * len(title))
    print(f"requests: {int(stats['requests'])}")
    print(f"ok:       {int(stats['ok'])}")
    print(f"errors:   {int(stats['errors'])} ({stats['error_pct']:.2f}%)")
    print(f"rps:      {stats['rps']:.2f}")
    print(f"mean ms:  {stats['mean_ms']:.1f}")
    print(f"p50 ms:   {stats['p50_ms']:.1f}")
    print(f"p95 ms:   {stats['p95_ms']:.1f}")
    print(f"p99 ms:   {stats['p99_ms']:.1f}")


def _write_json(path: str, payload: Dict[str, object]) -> None:
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)


def _write_csv(path: str, payload: Dict[str, object]) -> None:
    row = {
        "base_url": payload["base_url"],
        "version": payload["version"],
        "layer": payload["layer"],
        "style": payload["style"],
        "duration_seconds": payload["duration_seconds"],
        "concurrency": payload["concurrency"],
        "cap_interval_seconds": payload["cap_interval_seconds"],
        "restart_command": payload["restart_command"],
        "startup_getcapabilities_ms": payload["startup_getcapabilities_ms"],
        "startup_getcapabilities_ok": payload["startup_getcapabilities_ok"],
        "startup_getcapabilities_status": payload["startup_getcapabilities_status"],
        "startup_getmap_ms": payload["startup_getmap_ms"],
        "startup_getmap_ok": payload["startup_getmap_ok"],
        "startup_getmap_status": payload["startup_getmap_status"],
        "getmap_requests": payload["getmap"]["requests"],
        "getmap_ok": payload["getmap"]["ok"],
        "getmap_errors": payload["getmap"]["errors"],
        "getmap_error_pct": payload["getmap"]["error_pct"],
        "getmap_rps": payload["getmap"]["rps"],
        "getmap_mean_ms": payload["getmap"]["mean_ms"],
        "getmap_p50_ms": payload["getmap"]["p50_ms"],
        "getmap_p95_ms": payload["getmap"]["p95_ms"],
        "getmap_p99_ms": payload["getmap"]["p99_ms"],
        "getcap_requests": payload["getcapabilities"]["requests"],
        "getcap_ok": payload["getcapabilities"]["ok"],
        "getcap_errors": payload["getcapabilities"]["errors"],
        "getcap_error_pct": payload["getcapabilities"]["error_pct"],
        "getcap_rps": payload["getcapabilities"]["rps"],
        "getcap_mean_ms": payload["getcapabilities"]["mean_ms"],
        "getcap_p50_ms": payload["getcapabilities"]["p50_ms"],
        "getcap_p95_ms": payload["getcapabilities"]["p95_ms"],
        "getcap_p99_ms": payload["getcapabilities"]["p99_ms"],
    }

    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(row.keys()))
        writer.writeheader()
        writer.writerow(row)


def _run_restart_command(command: str, timeout_seconds: float) -> None:
    print("\nPreparing cold start")
    print("--------------------")
    print(f"running restart command: {command}")
    started = time.perf_counter()
    completed = subprocess.run(  # noqa: S603
        command,
        shell=True,  # noqa: S602
        check=False,
        capture_output=True,
        text=True,
        timeout=timeout_seconds,
    )
    elapsed_ms = (time.perf_counter() - started) * 1000.0
    if completed.returncode != 0:
        stderr = (completed.stderr or "").strip()
        stdout = (completed.stdout or "").strip()
        details = stderr or stdout or f"exit code {completed.returncode}"
        raise RuntimeError(f"Restart command failed: {details}")
    print(f"restart completed in {elapsed_ms:.1f} ms")


def _wait_for_url(url: str, timeout_seconds: float, interval_seconds: float, request_timeout: float) -> None:
    print(f"waiting for endpoint readiness: {url}")
    start = time.perf_counter()
    last_error = ""
    while (time.perf_counter() - start) < timeout_seconds:
        sample = _http_get(url, timeout=request_timeout)
        if sample.ok:
            print(f"endpoint ready after {(time.perf_counter() - start):.1f}s")
            return
        last_error = sample.error or f"status={sample.status}"
        time.sleep(interval_seconds)
    raise RuntimeError(f"Timed out waiting for endpoint readiness: {last_error}")


async def amain(args: argparse.Namespace) -> int:
    base_url = args.base_url.rstrip("?")
    ready_url = args.ready_url if args.ready_url else _build_root_url(base_url)

    if args.restart_command:
        _run_restart_command(args.restart_command, args.restart_timeout)
        _wait_for_url(
            url=ready_url,
            timeout_seconds=args.ready_timeout,
            interval_seconds=args.ready_interval,
            request_timeout=args.timeout,
        )

    scenario = discover_scenario(
        base_url=base_url,
        version=args.version,
        width=args.width,
        height=args.height,
        image_format=args.image_format,
        timeout=args.timeout,
    )

    print("Discovered WMS scenario")
    print("-----------------------")
    print(f"base_url:           {scenario.base_url}")
    print(f"version:            {scenario.version}")
    print(f"layer:              {scenario.layer}")
    print(f"style:              {scenario.style or '(default)'}")
    print(f"getcapabilities:    {scenario.getcapabilities_url}")
    print(f"getmap (sample):    {scenario.getmap_url}")
    print("\nCold-start timings")
    print("------------------")
    print(
        f"first GetCapabilities: {scenario.startup_getcapabilities_ms:.1f} ms "
        f"(status={scenario.startup_getcapabilities_status}, ok={scenario.startup_getcapabilities_ok})"
    )

    warmup = _http_get(scenario.getmap_url, timeout=args.timeout)
    if not warmup.ok:
        raise RuntimeError(f"GetMap warmup failed: {warmup.error or warmup.status}")
    print(f"first GetMap:          {warmup.latency_ms:.1f} ms (status={warmup.status}, ok={warmup.ok})")

    print("\nWarmup successful. Starting benchmark...")

    getmap_task = asyncio.to_thread(
        run_getmap_benchmark,
        scenario.getmap_url,
        args.duration,
        args.concurrency,
        args.timeout,
    )
    getcap_task = poll_getcapabilities(
        scenario.getcapabilities_url,
        args.duration,
        args.cap_interval,
        args.timeout,
    )

    (getmap_samples, getmap_wall), (getcap_samples, getcap_wall) = await asyncio.gather(getmap_task, getcap_task)

    getmap_stats = _stats(getmap_samples, getmap_wall)
    getcap_stats = _stats(getcap_samples, getcap_wall)

    payload: Dict[str, object] = {
        "base_url": scenario.base_url,
        "version": scenario.version,
        "layer": scenario.layer,
        "style": scenario.style,
        "duration_seconds": args.duration,
        "concurrency": args.concurrency,
        "cap_interval_seconds": args.cap_interval,
        "restart_command": args.restart_command,
        "startup_getcapabilities_ms": scenario.startup_getcapabilities_ms,
        "startup_getcapabilities_ok": scenario.startup_getcapabilities_ok,
        "startup_getcapabilities_status": scenario.startup_getcapabilities_status,
        "startup_getmap_ms": warmup.latency_ms,
        "startup_getmap_ok": warmup.ok,
        "startup_getmap_status": warmup.status,
        "getmap": getmap_stats,
        "getcapabilities": getcap_stats,
    }

    if args.output_json:
        _write_json(args.output_json, payload)
        print(f"\nWrote JSON results: {args.output_json}")

    if args.output_csv:
        _write_csv(args.output_csv, payload)
        print(f"Wrote CSV results:  {args.output_csv}")

    _print_report("GetMap results", getmap_stats)
    _print_report("GetCapabilities polling results", getcap_stats)

    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Benchmark WMS GetMap performance while asynchronously polling GetCapabilities"
    )
    parser.add_argument(
        "--base-url",
        default="http://127.0.0.1:5000/wms",
        help="Base WMS endpoint URL (default: http://127.0.0.1:5000/wms)",
    )
    parser.add_argument(
        "--version",
        default="1.3.0",
        choices=("1.1.1", "1.3.0"),
        help="WMS version used for discovery and GetMap requests",
    )
    parser.add_argument("--duration", type=int, default=30, help="Benchmark duration in seconds")
    parser.add_argument("--concurrency", type=int, default=8, help="Parallel GetMap workers")
    parser.add_argument("--cap-interval", type=float, default=0.5, help="Seconds between GetCapabilities polls")
    parser.add_argument("--width", type=int, default=256, help="GetMap width")
    parser.add_argument("--height", type=int, default=256, help="GetMap height")
    parser.add_argument("--image-format", default="image/png", help="GetMap format")
    parser.add_argument("--timeout", type=float, default=30.0, help="Per-request timeout in seconds")
    parser.add_argument("--restart-command", default="", help="Optional command executed before benchmark to force a cold start")
    parser.add_argument("--restart-timeout", type=float, default=120.0, help="Timeout in seconds for --restart-command")
    parser.add_argument("--ready-url", default="", help="Optional readiness URL checked after restart (defaults to site root, not WMS)")
    parser.add_argument("--ready-timeout", type=float, default=60.0, help="Max seconds to wait for endpoint readiness after restart")
    parser.add_argument("--ready-interval", type=float, default=1.0, help="Seconds between readiness checks")
    parser.add_argument("--output-json", default="", help="Optional JSON output file path")
    parser.add_argument("--output-csv", default="", help="Optional CSV output file path")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        return asyncio.run(amain(args))
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
