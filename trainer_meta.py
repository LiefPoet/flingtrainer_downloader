#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
从 风灵月影系单机修改器 EXE 中提取中文游戏名 / 英文名 / 项目数

原理：
  这类修改器的标题以 **UTF-16LE 原始宽字符串** 直接躺在 .rdata 里，格式固定：
      《雾锁王国（Enshrouded）》Early Access 十八项修改器
  程序运行时用内置正则 `《(.*?)（(.*?)）》(.*)\s(.*?)项修改器` 切分，
  第一段是中文名（UI 里橙色显示），第二段是英文名，最后是项目数。

  所以不需要加载资源、不需要跑起来，也不用版本信息 —— 直接扫二进制字符串即可。

用法：
    from trainer_meta import extract
    print(extract(r"xxx Trainer.exe"))
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------- 常量

# UTF-16LE 的“可打印宽字符”单元：ASCII 可见 + CJK 统一汉字 + CJK 标点 + 全角
_WIDE_UNIT = rb"(?:[\x20-\x7e]\x00|[\x00-\xff][\x4e-\x9f]|[\x00-\xff][\x30-\x33]|[\x00-\xff]\xff)"
_WIDE_RUN = re.compile(_WIDE_UNIT + rb"{4,}")

# 《中文名（English）》类型 数字项修改器
_TITLE_RE = re.compile(
    r"《(?P<cn>[^》（(]+)(?:[（(](?P<en>[^）)]+)[）)])?》"
    r"(?P<rest>[^\x00\n]{0,40}?)"
    r"(?P<items>[零一二三四五六七八九十百千两\d]+)项修改器"
)

# 兜底：没有书名号时，抓任何以“项修改器”结尾、含汉字的串
_LOOSE_RE = re.compile(r"^(?P<full>[^\x00\n]{4,80}?项修改器)")

_CJK = re.compile(r"[\u4e00-\u9fff]")


# ---------------------------------------------------------------- 字符串扫描

def scan_utf16(data: bytes, min_len: int = 4):
    """产出 (文件偏移, 文本)。逐段按 UTF-16LE 解码，跳过不可打印单元。"""
    for m in _WIDE_RUN.finditer(data):
        raw = m.group()
        # 规则可能从奇数位起跳，向右微调一位再试一次
        for shift in (0, 1):
            chunk = raw[shift:]
            if len(chunk) < min_len * 2:
                continue
            if len(chunk) % 2:
                chunk = chunk[:-1]
            try:
                txt = chunk.decode("utf-16-le")
            except UnicodeDecodeError:
                continue
            if sum(1 for c in txt if c.isprintable()) >= len(txt) * 0.9:
                yield m.start() + shift, txt


def scan_ansi(data: bytes, min_len: int = 4):
    """GBK（ANSI 编译的老版本修改器）兜底扫描。"""
    pat = re.compile(rb"(?:[\x81-\xfe][\x40-\xfe]|[\x20-\x7e]){4,}")
    for m in pat.finditer(data):
        try:
            txt = m.group().decode("gbk")
        except UnicodeDecodeError:
            continue
        if _CJK.search(txt):
            yield m.start(), txt


# ---------------------------------------------------------------- 提取

def extract(path: str | Path, *, want_offset: bool = False) -> dict | None:
    """
    返回:
    例：
        {"cn": "雾锁王国", "en": "Enshrouded", "type": "Early Access",
         "items": 18, "items_cn": "十八", "full": "《雾锁王国（Enshrouded）》Early Access 十八项修改器",
         "offset": 1025312, "encoding": "utf-16-le"}
    找不到返回 None。
    """
    data = Path(path).read_bytes()

    for encoding, scanner in (("utf-16-le", scan_utf16), ("gbk", scan_ansi)):
        best = None
        for off, txt in scanner(data):
            m = _TITLE_RE.search(txt)
            if m:
                cand = _build(m, off, encoding, txt)
            else:
                m2 = _LOOSE_RE.search(txt.strip())
                if not m2:
                    continue
                cand = {
                    "cn": _first_cjk_run(m2.group("full")),
                    "en": None,
                    "type": None,
                    "items": None,
                    "items_cn": None,
                    "full": m2.group("full"),
                    "offset": off,
                    "encoding": encoding,
                }
            # 越完整（有英文名、有项目数）越优先
            score = (cand["en"] is not None) + (cand["items"] is not None)
            if best is None or score > best[0]:
                best = (score, cand)
        if best:
            out = best[1]
            if not want_offset:
                out.pop("offset", None)
            return out

    return None


def _build(m: re.Match, off: int, encoding: str, txt: str) -> dict:
    items_cn = m.group("items")
    return {
        "cn": m.group("cn").strip(),
        "en": (m.group("en") or "").strip() or None,
        "type": m.group("rest").strip() or None,
        "items": _cn2int(items_cn),
        "items_cn": items_cn,
        "full": m.group(0),
        "offset": off,
        "encoding": encoding,
    }


def _first_cjk_run(s: str) -> str:
    runs = _CJK.findall(s)
    return "".join(runs)


_CN_DIGITS = {"零": 0, "一": 1, "二": 2, "两": 2, "三": 3, "四": 4,
              "五": 5, "六": 6, "七": 7, "八": 8, "九": 9}


def _cn2int(s: str) -> int | None:
    """中文数字转整数：'十八' -> 18，'二十' -> 20，'5' -> 5。"""
    if s.isdigit():
        return int(s)
    total, section, num = 0, 0, 0
    for ch in s:
        if ch in _CN_DIGITS:
            num = _CN_DIGITS[ch]
        elif ch == "十":
            section += (num or 1) * 10
            num = 0
        elif ch == "百":
            section += (num or 1) * 100
            num = 0
        elif ch == "千":
            section += (num or 1) * 1000
            num = 0
        else:
            return None
    return total + section + num


# ---------------------------------------------------------------- CLI

def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    for f in sys.argv[1:]:
        r = extract(f, want_offset=True)
        if r is None:
            print(f"[MISS] {f}")
            continue
        print(json.dumps(r, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
