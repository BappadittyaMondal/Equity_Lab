"""Surveillance Status Resolver (Phase 147).

Resolves ASM/ESM/GSM/T2T regulatory surveillance status for Indian equities.
Maintains a local SQLite/PostgreSQL `surveillance_status` table that can be
populated via REST API push or manual batch import.

When surveillance data is unavailable for a symbol, returns conservative
defaults (CLEAN with 20% circuit band) rather than failing closed, since
this is an analytical decision-support system (not live trading).
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from app.services.db import get_connection
from app.services.market_data import normalize_symbol

class SurveillanceResolver:
    @staticmethod
    def _ensure_table():
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS surveillance_status (
                symbol TEXT PRIMARY KEY,
                asm_stage TEXT DEFAULT 'CLEAN',
                gsm_stage TEXT DEFAULT 'CLEAN',
                esm_stage TEXT DEFAULT 'CLEAN',
                t2t_flag BOOLEAN DEFAULT 0,
                fo_ban_flag BOOLEAN DEFAULT 0,
                circuit_band_pct REAL DEFAULT 20.0,
                updated_at TEXT NOT NULL
            )
        """)
        conn.commit()
        conn.close()

    @staticmethod
    def resolve(symbol: str) -> Dict[str, Any]:
        SurveillanceResolver._ensure_table()
        norm_symbol = normalize_symbol(symbol)
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT asm_stage, gsm_stage, esm_stage, t2t_flag, fo_ban_flag, circuit_band_pct FROM surveillance_status WHERE symbol = ?", (norm_symbol,))
        row = cursor.fetchone()
        conn.close()

        if row:
            return {
                "asm_stage": row[0],
                "gsm_stage": row[1],
                "esm_stage": row[2],
                "t2t_flag": bool(row[3]),
                "fo_ban_flag": bool(row[4]),
                "circuit_band_pct": float(row[5])
            }
        
        return {
            "asm_stage": "CLEAN",
            "gsm_stage": "CLEAN",
            "esm_stage": "CLEAN",
            "t2t_flag": False,
            "fo_ban_flag": False,
            "circuit_band_pct": 20.0
        }

    @staticmethod
    def update(symbol: str, asm_stage: str = 'CLEAN', gsm_stage: str = 'CLEAN', esm_stage: str = 'CLEAN', t2t_flag: bool = False, fo_ban_flag: bool = False, circuit_band_pct: float = 20.0) -> bool:
        SurveillanceResolver._ensure_table()
        norm_symbol = normalize_symbol(symbol)
        conn = get_connection()
        cursor = conn.cursor()
        now = datetime.now(timezone.utc).isoformat()
        
        cursor.execute("""
            INSERT INTO surveillance_status 
            (symbol, asm_stage, gsm_stage, esm_stage, t2t_flag, fo_ban_flag, circuit_band_pct, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(symbol) DO UPDATE SET
                asm_stage=excluded.asm_stage,
                gsm_stage=excluded.gsm_stage,
                esm_stage=excluded.esm_stage,
                t2t_flag=excluded.t2t_flag,
                fo_ban_flag=excluded.fo_ban_flag,
                circuit_band_pct=excluded.circuit_band_pct,
                updated_at=excluded.updated_at
        """, (norm_symbol, asm_stage, gsm_stage, esm_stage, int(t2t_flag), int(fo_ban_flag), float(circuit_band_pct), now))
        
        conn.commit()
        conn.close()
        return True

    @staticmethod
    def bulk_update(records: List[Dict[str, Any]]) -> int:
        SurveillanceResolver._ensure_table()
        conn = get_connection()
        cursor = conn.cursor()
        now = datetime.now(timezone.utc).isoformat()
        count = 0
        
        for record in records:
            if "symbol" not in record:
                continue
            norm_symbol = normalize_symbol(record["symbol"])
            asm = record.get("asm_stage", "CLEAN")
            gsm = record.get("gsm_stage", "CLEAN")
            esm = record.get("esm_stage", "CLEAN")
            t2t = int(record.get("t2t_flag", False))
            fo_ban = int(record.get("fo_ban_flag", False))
            cb = float(record.get("circuit_band_pct", 20.0))
            
            cursor.execute("""
                INSERT INTO surveillance_status 
                (symbol, asm_stage, gsm_stage, esm_stage, t2t_flag, fo_ban_flag, circuit_band_pct, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(symbol) DO UPDATE SET
                    asm_stage=excluded.asm_stage,
                    gsm_stage=excluded.gsm_stage,
                    esm_stage=excluded.esm_stage,
                    t2t_flag=excluded.t2t_flag,
                    fo_ban_flag=excluded.fo_ban_flag,
                    circuit_band_pct=excluded.circuit_band_pct,
                    updated_at=excluded.updated_at
            """, (norm_symbol, asm, gsm, esm, t2t, fo_ban, cb, now))
            count += 1
            
        conn.commit()
        conn.close()
        return count

    @staticmethod
    def get_all_flagged() -> List[Dict[str, Any]]:
        SurveillanceResolver._ensure_table()
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT symbol, asm_stage, gsm_stage, esm_stage, t2t_flag, fo_ban_flag, circuit_band_pct, updated_at 
            FROM surveillance_status 
            WHERE asm_stage != 'CLEAN' 
               OR gsm_stage != 'CLEAN' 
               OR esm_stage != 'CLEAN' 
               OR t2t_flag = 1 
               OR fo_ban_flag = 1 
               OR circuit_band_pct < 20.0
        """)
        
        rows = cursor.fetchall()
        conn.close()
        
        results = []
        for row in rows:
            results.append({
                "symbol": row[0],
                "asm_stage": row[1],
                "gsm_stage": row[2],
                "esm_stage": row[3],
                "t2t_flag": bool(row[4]),
                "fo_ban_flag": bool(row[5]),
                "circuit_band_pct": float(row[6]),
                "updated_at": row[7]
            })
            
        return results
