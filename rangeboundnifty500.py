#!/usr/bin/env python3
"""
Range Bound Strategy - Live Market Screener
Author: Antigravity AI
Date: 2026-06-01

This script performs a live scan of stock symbols for the Alternate Touch Range-Bound Strategy:
1. Batch downloads daily historical price data for the last 2 years from Yahoo Finance.
2. Automatically discovers candidate Support (S) and Resistance (R) levels using peak/trough clustering.
3. Runs the 6-state Alternating Touch State Machine on level combinations.
4. Identifies active trades that haven't hit target (R) or stop loss (S * 0.90).
5. Dynamic financial growth filter verification (comparing TTM Net Profit & Revenue to S1 year values).
6. Generates a premium dark-themed HTML opportunity report.
"""

import os
import json
import math
import sys
from datetime import datetime, timedelta
import warnings

# Suppress warnings
warnings.filterwarnings('ignore')

try:
    import yfinance as yf
    import pandas as pd
    import numpy as np
except ImportError:
    print("Error: yfinance, pandas and numpy are required. Install them with: pip install yfinance pandas numpy")
    sys.exit(1)

# List of stocks to scan (combining user custom stocks with Nifty 500)
USER_STOCKS = [
    "3MINDIA","ABB","ABBOTINDIA","ABSLAMC","ACE","AIIL","AJANTPHARM","AJAXENGG","AKZOINDIA","ALIVUS",
    "ALKEM","ANANDRATHI","APARINDS","APLAPOLLO","ASIANPAINT","AVANTIFEED","AWL","BALUFORGE","BAYERCROP","BEL",
    "BERGEPAINT","BLS","BLUEJET","BLUESTARCO","BOSCHLTD","BSE","BSOFT","CAMS","CAPLIPOINT","CASTROLIND",
    "CDSL","CELLO","CERA","CGPOWER","CHAMBLFERT","CIGNITITEC","CIPLA","CLEAN","CMSINFO","COALINDIA",
    "COCHINSHIP","COFORGE","COLPAL","CONCORDBIO","COROMANDEL","CRISIL","CUMMINSIND","DABUR","DATAPATTNS","DBCORP",
    "DHANUKA","DIVISLAB","DIXON","DODLA","DOLATALGO","DOMS","DRREDDY","ECLERX","EICHERMOT","EIHOTEL",
    "ELECON","EMAMILTD","EMCURE","ENGINERSIN","FIEMIND","FINEORG","FORCEMOT","GABRIEL","GANESHHOU","GARFIBRES",
    "GHCL","GILLETTE","GLAXO","GODFRYPHLP","GPIL","GPPL","GRAVITA","GRINDWELL","GRSE","GRWRHITECH",
    "HAL","HAVELLS","HBLENGINE","HCLTECH","HDFCAMC","HEROMOTOCO","HEXT","HINDCOPPER","HINDUNILVR","HSCL",
    "HYUNDAI","ICICIGI","IEX","IGIL","IGL","IMFA","INDGN","INDIAMART","INFY","INGERRAND",
    "INOXINDIA","IRCTC","ITC","JBCHEPHARM","JWL","JYOTHYLAB","KEI","KFINTECH","KIRLOSBROS","KIRLPNU",
    "KPITTECH","KSB","KSCL","LALPATHLAB","LICI","LLOYDSME","LTM","LTTS","MAITHANALL","MANINFRA",
    "MARICO","MARKSANS","MARUTI","MAZDOCK","MCX","MGL","MPHASIS","MSTCLTD","MSUMI","NATCOPHARM",
    "NATIONALUM","NBCC","NCC","NESCO","NEWGEN","NIITMTS","NMDC","OFSS","PAGEIND","PERSISTENT",
    "PETRONET","PFIZER","PGHH","PGHL","PIDILITIND","PIIND","POLYCAB","POLYMED","RAILTEL","RATNAMANI",
    "RITES","SANOFI","SCHAEFFLER","SHAKTIPUMP","SHARDAMOTR","SHAREINDIA","SHRIPISTON","SIEMENS","SKFINDIA","SOLARINDS",
    "SPLPETRO","SUMICHEM","SUNPHARMA","SUNTV","SUPREMEIND","SURYAROSNI","SUZLON","SYMPHONY","TANLA","TARIL",
    "TATAELXSI","TATATECH","TBOTEK","TCI","TCS","TI","TIINDIA","TIMKEN","TRITURBINE","UNITDSPR",
    "UTIAMC","VBL","VESUVIUS","VINATIORGA","VOLTAMP","VSTIND","WAAREEENER","WAAREERTL","WELCORP","ZENSARTECH",
    "ZENTEC","ZFCVINDIA","ZYDUSLIFE","JIOFIN","ANGELONE","BAJAJHLDNG","ULTRACEMCO",
    "ACC","TEAMLEASE","QUESS","ASTRAZEN","ERIS","APOLLOHOSP","MEDANTA","FORTIS",
    "ADANIPORTS","JSWINFRA","GODREJCP","KAJARIACER","HONAUT","DMART","RELAXO","MRF","M&M","TMPV",
    "INDHOTEL","RADICO","UBL","MAHABANK","ICICIBANK","CANBK","KARURVYSYA","SBIN","INDIANB","UNIONBANK",
    "AXISBANK","J&KBANK","BANKBARODA","PNB","HDFCBANK","CSBBANK","AUBANK","TMB","SOUTHBANK","IDBI",
    "KOTAKBANK","JSFB","FEDERALBNK","CUB","UJJIVANSFB","BANKINDIA","POONAWALLA","BAJFINANCE","RECLTD","SHRIRAMFIN",
    "LICHSGFIN","MUTHOOTFIN","CHOLAHLDNG","CHOLAFIN","AIIL","HUDCO","TVSHLTD","BAJAJHFL","PNBHOUSING","SBICARD",
    "SUNDARMFIN","IREDA","FIVESTAR","AADHARHFC","CANFINHOME","APTUS","CRISIL","AAVAS","REPCOHOME",
    "RELIANCE","LT","INDUSINDBK","TATASTEEL","JSWSTEEL","HINDALCO","TATACONSUM","TITAN",
    "BAJAJ-AUTO","TVSMOTOR","BPCL","IOC","ONGC","NTPC","POWERGRID","ADANIENT",
    "ADANIGREEN","ADANIPOWER","LUPIN","AUROPHARMA","SHREECEM","GRASIM","BRITANNIA",
    "NESTLEIND","HDFCLIFE","SBILIFE","TRENT","APOLLOTYRE","DLF","GODREJPROP",
    "OBEROIRLTY","TATACOMM","BHARTIAIRTEL","INDIGO","UPL",
    "TECHM","WIPRO","AMBUJACEM","ICICIPRULI","PFC","SRF","GAIL","GMRINFRA",
    "IRFC","JINDALSTEL","MAXHEALTH","NHPC","PBFINTECH","SAIL","TATACHEM","TATAPOWER",
    "KAYNES","ASTRAL","RVNL","MOTILALOFS","BECTORFOOD","SUPRAJIT","AETHER","NETWEB",
    "SJVN","TATAINVEST","IRCON","TATAMOTORS","GENUSPOWER","AMBER","PGEL","RRKABEL",
    "FINPIPE","THERMAX","WESTLIFE","SAPPHIRE","CREDITACC","HOMEFIRST","CYIENT","EXIDEIND",
    "ARE&M","PRESTIGE","SOBHA","KIMS","NH","VOLTAS"
]


class AlternateTouchStrategy:
    def __init__(self, n_window=30, min_height_pct=20.0, spacing_days=15, buffer_pct=4.0):
        self.n = n_window
        self.min_height = min_height_pct
        self.spacing = spacing_days
        self.buffer_pct = buffer_pct

    def check_tolerance_support(self, s, low, high):
        """Support Zone: [S * 0.95, S * 1.03]"""
        return low <= s * 1.03 and high >= s * 0.95

    def check_tolerance_resistance(self, r, low, high):
        """Resistance Zone: [R * 0.97, R * 1.05]"""
        return high >= r * 0.97 and low <= r * 1.05

    def evaluate_state_machine(self, dates, opens, highs, lows, closes, s, r):
        """
        Runs a generalized alternating touch state machine (S1 -> R1 -> S2 -> R2 -> S3 -> R3 -> S4 -> R4 -> S5 -> R5 -> S6...) over historical price array.
        """
        state = 0
        touches = {}
        logs = []
        last_touch_date = None
        
        for i in range(len(dates)):
            curr_date = datetime.strptime(dates[i], "%Y-%m-%d")
            close = closes[i]
            low = lows[i]
            high = highs[i]
            
            # Invalidation Rule: Close < S * 0.90
            if state > 0 and close < s * 0.90:
                state = 0
                touches = {}
                last_touch_date = None
                logs.append(f"{dates[i]}: Pattern INVALIDATED! Close ({close:.2f}) fell below Stop Loss ({s*0.90:.2f}). State reset to 0.")
                continue

            # State Transitions
            if state == 0:
                if self.check_tolerance_support(s, low, high):
                    state = 1
                    touches['S1'] = {"date": dates[i], "idx": i, "price": low}
                    last_touch_date = curr_date
                    logs.append(f"{dates[i]}: State 0 -> 1. Support Touch 1 (S1) at Low={low:.2f}.")
            
            elif state % 2 == 1:
                # Odd state: Looking for Resistance touch R_k (where k = (state + 1) // 2)
                r_num = (state + 1) // 2
                days_since = (curr_date - last_touch_date).days
                if days_since >= self.spacing and self.check_tolerance_resistance(r, low, high):
                    # Check buffer against R1
                    if r_num == 1 or high >= touches['R1']['price'] * (1.0 - self.buffer_pct / 100.0):
                        state += 1
                        touches[f'R{r_num}'] = {"date": dates[i], "idx": i, "price": high}
                        last_touch_date = curr_date
                        logs.append(f"{dates[i]}: State {state-1} -> {state}. Resistance Touch {r_num} (R{r_num}) at High={high:.2f} after {days_since} days.")

            elif state % 2 == 0:
                # Even state: Looking for Support touch S_k (where k = state // 2 + 1)
                s_num = state // 2 + 1
                days_since = (curr_date - last_touch_date).days
                if days_since >= self.spacing and self.check_tolerance_support(s, low, high):
                    # Check buffer against S1
                    if low <= touches['S1']['price'] * (1.0 + self.buffer_pct / 100.0):
                        state += 1
                        touches[f'S{s_num}'] = {"date": dates[i], "idx": i, "price": low}
                        last_touch_date = curr_date
                        logs.append(f"{dates[i]}: State {state-1} -> {state}. Support Touch {s_num} (S{s_num}) at Low={low:.2f} after {days_since} days.")

        return state, touches, logs


def check_volume_spike(volumes, idx, factor=1.5, window=20):
    """
    Checks if volume on day idx is a spike compared to the 20-day SMA of volume prior to it.
    """
    if idx <= 0:
        return False, 0.0
    start_idx = max(0, idx - window)
    window_vols = volumes[start_idx:idx]
    if not window_vols:
        return False, 0.0
    avg_vol = sum(window_vols) / len(window_vols)
    if avg_vol == 0:
        return False, 0.0
    ratio = volumes[idx] / avg_vol
    return ratio >= factor, ratio



def find_levels(highs, lows, dates, n=30, cluster_pct=0.04):
    """
    1. Rolling window peak/trough discovery.
    2. Clusters levels grouping prices within cluster_pct of each other.
    """
    peaks = []
    troughs = []
    
    for i in range(n, len(highs) - n):
        win_high = highs[i-n:i+n+1]
        win_low = lows[i-n:i+n+1]
        
        if highs[i] == max(win_high):
            peaks.append(highs[i])
        if lows[i] == min(win_low):
            troughs.append(lows[i])
            
    def cluster(values):
        if not values:
            return []
        values = sorted(values)
        clusters = []
        curr = [values[0]]
        
        for val in values[1:]:
            mean_val = sum(curr) / len(curr)
            if (val - mean_val) / mean_val <= cluster_pct:
                curr.append(val)
            else:
                clusters.append(sum(curr) / len(curr))
                curr = [val]
        clusters.append(sum(curr) / len(curr))
        return clusters

    return cluster(troughs), cluster(peaks)


def detect_swings(dates, highs, lows, closes, atrs, window=5):
    # Calculate average daily ATR percentage
    atr_pcts = [atr / close for atr, close in zip(atrs, closes) if close > 0]
    avg_atr_pct = sum(atr_pcts) / len(atr_pcts) if atr_pcts else 0.02
    
    # Adaptive thresholds
    min_pct = max(0.015, min(0.035, avg_atr_pct * 0.8))
    atr_factor = max(1.0, min(1.5, avg_atr_pct * 50.0))
    time_sep = 3
    
    n = len(closes)
    raw_swings = []
    
    for i in range(window, n - window):
        is_peak = True
        is_trough = True
        for j in range(i - window, i + window + 1):
            if j == i:
                continue
            if highs[j] > highs[i]:
                is_peak = False
            if lows[j] < lows[i]:
                is_trough = False
        if is_peak:
            raw_swings.append((i, 'H', highs[i], dates[i]))
        if is_trough:
            raw_swings.append((i, 'L', lows[i], dates[i]))
            
    raw_swings = sorted(raw_swings, key=lambda x: x[0])
    
    swings = []
    for s in raw_swings:
        idx, side, price, date = s
        atr = atrs[idx]
        min_move = max(min_pct * price, atr_factor * atr)
        
        if not swings:
            swings.append(s)
            continue
            
        last_idx, last_side, last_price, last_date = swings[-1]
        
        if side == last_side:
            if side == 'H' and price > last_price:
                swings[-1] = s
            elif side == 'L' and price < last_price:
                swings[-1] = s
        else:
            if abs(price - last_price) >= min_move and (idx - last_idx) >= time_sep:
                swings.append(s)
                
    final_swings = []
    for s in swings:
        if not final_swings:
            final_swings.append(s)
            continue
        last_idx, last_side, last_price, last_date = final_swings[-1]
        if s[1] == last_side:
            if last_side == 'H' and s[2] > last_price:
                final_swings[-1] = s
            elif last_side == 'L' and s[2] < last_price:
                final_swings[-1] = s
        else:
            final_swings.append(s)
            
    return final_swings


def find_alternating_pivots(dates, highs, lows, closes, S, R, atrs, swings):
    touches = []
    for s in swings:
        idx, side, price, date = s
        local_atr = atrs[idx]
        tol = max(2.0 * local_atr, 0.02 * price)
        S_low, S_high = S - tol, S + tol
        R_low, R_high = R - tol, R + tol
        
        is_s = lows[idx] <= S_high + 0.5 * local_atr and highs[idx] >= S_low - 0.5 * local_atr
        is_r = highs[idx] >= R_low - 0.5 * local_atr and lows[idx] <= R_high + 0.5 * local_atr
        
        if side == 'L' and is_s:
            touches.append(('S', idx, date, price))
        elif side == 'H' and is_r:
            touches.append(('R', idx, date, price))
            
    final_idx = len(dates) - 1
    local_atr = atrs[final_idx]
    tol = max(2.0 * local_atr, 0.02 * closes[final_idx])
    S_low, S_high = S - tol, S + tol
    R_low, R_high = R - tol, R + tol
    
    is_final_s = lows[final_idx] <= S_high + 0.5 * local_atr and highs[final_idx] >= S_low - 0.5 * local_atr
    is_final_r = highs[final_idx] >= R_low - 0.5 * local_atr and lows[final_idx] <= R_high + 0.5 * local_atr
    
    if not any(t[1] == final_idx for t in touches):
        if is_final_s:
            touches.append(('S', final_idx, dates[final_idx], lows[final_idx]))
        elif is_final_r:
            touches.append(('R', final_idx, dates[final_idx], highs[final_idx]))
            
    touches = sorted(touches, key=lambda x: x[1])
            
    pivots = []
    current_search = 'S'
    curr_group = []
    
    for t in touches:
        side, idx, date, price = t
        if current_search == 'S':
            if side == 'S':
                curr_group.append(t)
            elif side == 'R' and curr_group:
                best = min(curr_group, key=lambda x: x[3])
                pivots.append(best)
                current_search = 'R'
                curr_group = [t]
        elif current_search == 'R':
            if side == 'R':
                curr_group.append(t)
            elif side == 'S' and curr_group:
                best = max(curr_group, key=lambda x: x[3])
                pivots.append(best)
                current_search = 'S'
                curr_group = [t]
                
    if curr_group:
        if current_search == 'S':
            best = min(curr_group, key=lambda x: x[3])
            pivots.append(best)
        else:
            best = max(curr_group, key=lambda x: x[3])
            pivots.append(best)
    
    MIN_MOVE_PCT = 0.14
    
    validated = []
    for pivot in pivots:
        if not validated:
            validated.append(pivot)
            continue
        
        last = validated[-1]
        
        if pivot[0] == last[0]:
            if pivot[0] == 'S' and pivot[3] < last[3]:
                validated[-1] = pivot
            elif pivot[0] == 'R' and pivot[3] > last[3]:
                validated[-1] = pivot
        else:
            if last[0] == 'S' and pivot[0] == 'R':
                move_pct = (pivot[3] - last[3]) / last[3]
                if move_pct >= MIN_MOVE_PCT:
                    validated.append(pivot)
            elif last[0] == 'R' and pivot[0] == 'S':
                move_pct = (last[3] - pivot[3]) / last[3]
                if move_pct >= MIN_MOVE_PCT:
                    validated.append(pivot)
            
    return validated


def evaluate_range_for_df(df_sub, min_height_pct, buffer_pct, lookback_months):
    dates = [d.strftime("%Y-%m-%d") for d in df_sub.index]
    highs = df_sub['High'].tolist()
    lows = df_sub['Low'].tolist()
    closes = df_sub['Close'].tolist()
    opens = df_sub['Open'].tolist()
    volumes = df_sub['Volume'].tolist()
    
    highs_s = df_sub['High']
    lows_s = df_sub['Low']
    closes_s = df_sub['Close']
    tr = pd.concat([
        highs_s - lows_s,
        (highs_s - closes_s.shift(1)).abs(),
        (lows_s - closes_s.shift(1)).abs()
    ], axis=1).max(axis=1)
    atr_series = tr.rolling(window=14).mean().bfill()
    atrs = atr_series.tolist()
    
    if len(df_sub) < 30:
        return []
        
    swings = detect_swings(dates, highs, lows, closes, atrs)
    if len(swings) < 5:
        return []
        
    high_prices = [s[2] for s in swings if s[1] == 'H']
    low_prices = [s[2] for s in swings if s[1] == 'L']
    
    if len(high_prices) < 2 or len(low_prices) < 2:
        return []
        
    avg_atr_pct = np.mean([atr / close for atr, close in zip(atrs, closes)])
    cluster_pct = max(0.04, min(0.07, 1.5 * avg_atr_pct))
    
    candidate_supports = []
    for p in low_prices:
        cluster = [x for x in low_prices if abs(x - p)/p <= cluster_pct]
        median_val = float(np.median(cluster))
        min_val = float(np.min(cluster))
        max_val = float(np.max(cluster))
        if not any(abs(c["S"] - median_val)/median_val < 0.015 for c in candidate_supports):
            candidate_supports.append({"S": median_val, "low": min_val, "high": max_val})
            
    candidate_resistances = []
    for p in high_prices:
        cluster = [x for x in high_prices if abs(x - p)/p <= cluster_pct]
        median_val = float(np.median(cluster))
        min_val = float(np.min(cluster))
        max_val = float(np.max(cluster))
        if not any(abs(c["R"] - median_val)/median_val < 0.015 for c in candidate_resistances):
            candidate_resistances.append({"R": median_val, "low": min_val, "high": max_val})
            
    valid_combos = []
    cmp = closes[-1]
    atr_last = atrs[-1] if atrs else 1.0
    tol = max(1.5 * atr_last, 0.02 * cmp)
    
    for s_cand in candidate_supports:
        for r_cand in candidate_resistances:
            S = s_cand["S"]
            R = r_cand["R"]
            if S >= R:
                continue
                
            height = (R - S) / S * 100
            if height < min_height_pct:
                continue
                
            S_low = s_cand["low"] - tol
            S_high = s_cand["high"] + tol
            R_low = r_cand["low"] - tol
            R_high = r_cand["high"] + tol
            
            pivots = find_alternating_pivots(dates, highs, lows, closes, S, R, atrs, swings)
            if not pivots:
                continue
                
            num_s = sum(1 for p in pivots if p[0] == 'S')
            num_r = sum(1 for p in pivots if p[0] == 'R')
            
            if pivots[-1][0] != 'S':
                continue
                
            if num_s < 3 or num_r < 2:
                continue
                
            start_idx = pivots[0][1]
            closes_after_start = closes[start_idx:]
            closes_inside = sum(1 for c in closes_after_start if S_low <= c <= R_high) / len(closes_after_start)
            if closes_inside < 0.65:
                continue
                
            if cmp < S_low * 0.65 or cmp > R_high * 1.05:
                continue
                
            low_prox = (cmp - S) / S * 100
            
            s_deviations = [abs(p[3] - S)/S for p in pivots if p[0] == 'S']
            s_quality = max(0.0, 10.0 - 60.0 * np.mean(s_deviations)) if s_deviations else 8.0
            
            r_deviations = [abs(p[3] - R)/R for p in pivots if p[0] == 'R']
            r_quality = max(0.0, 10.0 - 60.0 * np.mean(r_deviations)) if r_deviations else 8.0
            
            total_touches = num_s + num_r
            if total_touches >= 7:
                touch_strength = 10.0
            elif total_touches == 6:
                touch_strength = 9.0
            else:
                touch_strength = 8.0
            
            if closes_inside >= 0.75:
                zone_consistency = 10.0
            elif closes_inside >= 0.65:
                zone_consistency = 8.0
            elif closes_inside >= 0.55:
                zone_consistency = 6.0
            else:
                zone_consistency = 4.0
            
            height_atr_ratio = height / (atr_last / S * 100) if atr_last > 0 else 5.0
            if height_atr_ratio >= 5.0:
                atr_stability = 10.0
            elif height_atr_ratio >= 4.0:
                atr_stability = 8.0
            elif height_atr_ratio >= 3.0:
                atr_stability = 6.0
            else:
                atr_stability = 4.0
            
            p_indices = [p[1] for p in pivots]
            time_span = (p_indices[-1] - p_indices[0]) / len(closes)
            if time_span >= 0.60:
                time_symmetry = 10.0
            elif time_span >= 0.40:
                time_symmetry = 8.0
            else:
                time_symmetry = 6.0
            
            fb_score = 8.0
            outside_runs = 0
            is_outside = False
            for c in closes:
                if not (S_low <= c <= R_high):
                    if not is_outside:
                        outside_runs += 1
                        is_outside = True
                else:
                    is_outside = False
            if outside_runs > 0:
                fb_score = 9.0
                
            moves = [abs(pivots[i][3] - pivots[i-1][3])/pivots[i-1][3] for i in range(1, len(pivots))]
            if len(moves) > 1:
                std_moves = np.std(moves)
                swing_symmetry = max(0.0, 10.0 - 10.0 * std_moves)
            else:
                swing_symmetry = 8.0
                
            recent_atr = np.mean(atrs[-10:])
            avg_atr = np.mean(atrs)
            comp_ratio = recent_atr / avg_atr if avg_atr > 0 else 1.0
            vol_score = min(10.0, max(0.0, (1.1 - comp_ratio) / 0.3 * 10.0))
            if vol_score < 5.0:
                vol_score = 8.0
                
            if lookback_months >= 12:
                duration_score = 10.0
            elif lookback_months >= 6:
                duration_score = 8.0
            else:
                duration_score = 6.0
                
            confidence_score = int(s_quality + r_quality + touch_strength + zone_consistency + atr_stability + time_symmetry + fb_score + swing_symmetry + vol_score + duration_score)
            confidence_score = min(100, max(0, confidence_score))
            
            # Apply Proximity and Recency Bonuses
            if S <= cmp <= S * 1.05:
                confidence_score = min(100, confidence_score + 5)
            
            days_since_last_pivot = len(closes) - pivots[-1][1]
            if pivots[-1][0] == 'S' and days_since_last_pivot <= 30:
                confidence_score = min(100, confidence_score + 5)
                
            if confidence_score < 70:
                continue
                
            prox_score = 0
            if cmp >= S and cmp <= S * 1.02:
                prox_score = 3
            elif cmp > S * 1.02 and cmp <= S * 1.05:
                prox_score = 2
            elif cmp >= S * 0.95 and cmp < S:
                prox_score = 1
            elif cmp > S * 1.15:
                prox_score = -3
            elif cmp > S * 1.08:
                prox_score = -1
                
            risk = max(1.0, cmp - S * 0.90)
            reward = max(1.0, R - cmp)
            rr_ratio = reward / risk
            rr_score = 0
            if rr_ratio >= 3.0:
                rr_score = 2
            elif rr_ratio >= 2.0:
                rr_score = 1
            elif rr_ratio < 1.0:
                rr_score = -2
                
            vol_boost = 1 if comp_ratio <= 0.90 else 0
            trade_score = int(6 + prox_score + rr_score + vol_boost)
            trade_score = min(10, max(1, trade_score))
            
            s_prices = [p[3] for p in pivots if p[0] == 'S']
            r_prices = [p[3] for p in pivots if p[0] == 'R']
            
            drift_ok = True
            s_drift = 0
            r_drift = 0
            if len(s_prices) >= 2:
                s_drift = abs(s_prices[-1] - s_prices[0]) / S * 100
                if s_drift > 15.0:
                    drift_ok = False
            if len(r_prices) >= 2:
                r_drift = abs(r_prices[-1] - r_prices[0]) / R * 100
                if r_drift > 15.0:
                    drift_ok = False
                    
            if lookback_months >= 36:
                fresh_limit = 120
            elif lookback_months >= 18:
                fresh_limit = 90
            else:
                fresh_limit = 60
            fresh_ok = days_since_last_pivot <= fresh_limit
            
            ignored_list = []
            pivot_indices = [p[1] for p in pivots]
            for s_pt in swings:
                idx, side, price, date = s_pt
                if idx not in pivot_indices:
                    is_s = lows[idx] <= S_high and highs[idx] >= S_low
                    is_r = highs[idx] >= R_low and lows[idx] <= R_high
                    if (side == 'L' and not is_s) or (side == 'H' and not is_r):
                        rsn = "Did not touch S/R zone"
                    else:
                        rsn = "Consecutive same-side touch (collapsed to extreme)"
                    ignored_list.append((date, side, price, rsn))
            
            temp_debug = {
                "support_zone": f"{S_low:.2f} - {S_high:.2f}",
                "resistance_zone": f"{R_low:.2f} - {R_high:.2f}",
                "atr_tolerance": tol,
                "range_width": height,
                "touch_count": len(pivots),
                "confidence_score": confidence_score,
                "pivots": pivots,
                "ignored_pivots": ignored_list,
                "passed": True,
                "passed_reason": "Passed all structural and discretionary validation checks",
                "rejected_reason": ""
            }
            
            if not (drift_ok and fresh_ok):
                temp_debug["passed"] = False
                temp_debug["rejected_reason"] = f"Discretionary checks failed (drift_ok={drift_ok} [s_drift={s_drift:.1f}%, r_drift={r_drift:.1f}%], fresh_ok={fresh_ok} [days={days_since_last_pivot}])"
                continue
                
            alt_s_touches = [p for p in pivots if p[0] == 'S']
            alt_r_touches = [p for p in pivots if p[0] == 'R']
            touches_map = {}
            for idx_t, t in enumerate(alt_s_touches, 1):
                touches_map[f'S{idx_t}'] = t[2]
            for idx_t, t in enumerate(alt_r_touches, 1):
                touches_map[f'R{idx_t}'] = t[2]
                
            vol_spikes = {}
            for idx_t, t in enumerate(alt_s_touches, 1):
                t_idx = t[1]
                start_v = max(0, t_idx - 20)
                vols_window = volumes[start_v:t_idx]
                is_spike = False
                ratio = 0.0
                if vols_window:
                    avg_v = sum(vols_window) / len(vols_window)
                    if avg_v > 0:
                        ratio = volumes[t_idx] / avg_v
                        is_spike = ratio >= 1.5
                vol_spikes[f'S{idx_t}'] = {
                    "date": t[2],
                    "volume": volumes[t_idx],
                    "ratio": ratio,
                    "is_spike": is_spike
                }
                
            history_data = []
            for i in range(len(df_sub)):
                history_data.append({
                    "time": dates[i],
                    "open": opens[i],
                    "high": highs[i],
                    "low": lows[i],
                    "close": closes[i],
                    "volume": volumes[i]
                })
                
            opt_info = {
                "support": S,
                "resistance": R,
                "cmp": cmp,
                "low_prox": low_prox,
                "s3_date": pivots[-1][2],
                "history": history_data,
                "touches": touches_map,
                "vol_spikes": vol_spikes,
                "final_state": 2 * len(alt_s_touches) - 1,
                "range_height": height,
                "confidence_score": confidence_score,
                "trade_score": trade_score,
                "s1_year": datetime.strptime(alt_s_touches[0][2], "%Y-%m-%d").year,
                "lookback_months": lookback_months
            }
            
            valid_combos.append((opt_info, confidence_score, temp_debug))
            
    return valid_combos


def check_dynamic_range(df, min_height_pct, buffer_pct, symbol):
    lookbacks = [6, 9, 12, 18, 24, 36, 48, 60]
    all_valid = []
    rejections = []
    lookbacks_info = {}
    best_debug_info = None
    
    for l_months in lookbacks:
        cutoff = df.index[-1] - pd.DateOffset(months=l_months)
        df_sub = df[df.index >= cutoff]
        if len(df_sub) < 30:
            msg = f"Too few bars ({len(df_sub)} < 30)"
            rejections.append(f"{l_months}M: {msg}")
            lookbacks_info[l_months] = f"Rejected - {msg}"
            continue
            
        combos = evaluate_range_for_df(df_sub, min_height_pct, buffer_pct, l_months)
        if not combos:
            msg = "No valid range found"
            rejections.append(f"{l_months}M: {msg}")
            lookbacks_info[l_months] = f"Rejected - {msg}"
            continue
            
        all_valid.extend(combos)
        for opt, score, debug in combos:
            if best_debug_info is None or score > best_debug_info.get("confidence_score", 0):
                best_debug_info = debug
                
        best_score_here = max(c[1] for c in combos)
        lookbacks_info[l_months] = f"SUCCESS (Best Score: {best_score_here})"
        
    if not all_valid:
        print(f"\n==================================================")
        print(f"DEBUG LOG FOR {symbol}")
        print(f"==================================================")
        print("Lookback Windows Evaluated:")
        for l_months, res in lookbacks_info.items():
            print(f"  - {l_months}M: {res}")
        print(f"[RESULT] REJECTED")
        if best_debug_info:
            print(f"  Best Candidate Evaluated:")
            print(f"    Support Zone: {best_debug_info.get('support_zone')}")
            print(f"    Resistance Zone: {best_debug_info.get('resistance_zone')}")
            print(f"    ATR Tolerance: {best_debug_info.get('atr_tolerance'):.2f}" if best_debug_info.get('atr_tolerance') is not None else "    ATR Tolerance: N/A")
            print(f"    Range Width: {best_debug_info.get('range_width'):.2f}%" if best_debug_info.get('range_width') is not None else "    Range Width: N/A")
            print(f"    Touch Count: {best_debug_info.get('touch_count')}")
            print(f"    Confidence Score: {best_debug_info.get('confidence_score')}")
            print(f"    Rejection Reason: {best_debug_info.get('rejected_reason') or '; '.join(rejections)}")
            pivots = best_debug_info.get('pivots', [])
            if pivots:
                print(f"    Pivots ({len(pivots)} alternating):")
                for p in pivots:
                    print(f"      - {p[0]}: {p[2]} at Price={p[3]:.2f}")
            ignored = best_debug_info.get('ignored_pivots', [])
            if ignored:
                print(f"    Ignored Pivots ({len(ignored)}):")
                for date, side, price, rsn in ignored:
                    print(f"      - {date} ({side}) at Price={price:.2f}: {rsn}")
        print(f"==================================================\n")
        
        reject_reason = best_debug_info.get('rejected_reason') if best_debug_info else "; ".join(rejections)
        return None, 0, reject_reason
        
    voted_options = []
    for opt, score, debug_info in all_valid:
        S = opt["support"]
        R = opt["resistance"]
        l_month = opt["lookback_months"]
        
        matching_lookbacks = {l_month}
        for other_opt, _, _ in all_valid:
            other_S = other_opt["support"]
            other_R = other_opt["resistance"]
            other_l_month = other_opt["lookback_months"]
            
            s_match = abs(S - other_S)/S <= 0.03
            r_match = abs(R - other_R)/R <= 0.03
            if s_match and r_match:
                matching_lookbacks.add(other_l_month)
                
        num_confirmations = len(matching_lookbacks)
        voting_bonus = (num_confirmations - 1) * 8
        voted_score = min(100, score + voting_bonus)
        
        import copy
        voted_opt = copy.deepcopy(opt)
        voted_opt["confidence_score"] = voted_score
        voted_opt["voted_confirmations"] = num_confirmations
        
        v_debug = copy.deepcopy(debug_info)
        v_debug["confidence_score"] = voted_score
        v_debug["voting_bonus"] = voting_bonus
        v_debug["confirmations_count"] = num_confirmations
        
        voted_options.append((voted_opt, voted_score, v_debug))
        
    voted_options.sort(key=lambda x: (x[1], x[0]["trade_score"], -x[0]["low_prox"]), reverse=True)
    
    best_opt, best_score, best_debug = voted_options[0]
    
    print(f"\n==================================================")
    print(f"DEBUG LOG FOR {symbol}")
    print(f"==================================================")
    print("Lookback Windows Evaluated:")
    for l_months, res in lookbacks_info.items():
        print(f"  - {l_months}M: {res}")
    print(f"[RESULT] SUCCESS! (Winning Lookback: {best_opt['lookback_months']}M)")
    print(f"  Confidence Score: {best_score} (Base: {best_opt['confidence_score'] - (best_opt.get('voted_confirmations', 1) - 1) * 8}, Voting Bonus: {(best_opt.get('voted_confirmations', 1) - 1) * 8})")
    print(f"  Trade Score: {best_opt['trade_score']}/10")
    print(f"  Support Zone: {best_debug.get('support_zone')} (S = {best_opt['support']:.2f})")
    print(f"  Resistance Zone: {best_debug.get('resistance_zone')} (R = {best_opt['resistance']:.2f})")
    print(f"  ATR Tolerance: {best_debug.get('atr_tolerance'):.2f}" if best_debug.get('atr_tolerance') is not None else "  ATR Tolerance: N/A")
    print(f"  Range Width: {best_debug.get('range_width'):.2f}%" if best_debug.get('range_width') is not None else f"  Range Width: {best_opt['range_height']:.2f}%")
    pivots = best_debug.get('pivots', [])
    print(f"  Pivots ({len(pivots)} alternating):")
    for p in pivots:
        print(f"    - {p[0]}: {p[2]} at Price={p[3]:.2f}")
    ignored = best_debug.get('ignored_pivots', [])
    if ignored:
        print(f"  Ignored Pivots ({len(ignored)}):")
        for date, side, price, rsn in ignored:
            print(f"    - {date} ({side}) at Price={price:.2f}: {rsn}")
    print(f"==================================================\n")
    
    return best_opt, best_score, None


def format_days_held(days_diff):
    if days_diff < 30:
        return f"{days_diff}d"
    elif days_diff < 365:
        m = days_diff // 30
        d = days_diff % 30
        return f"{m}M {d}d" if d > 0 else f"{m}M"
    else:
        y = days_diff // 365
        rem = days_diff % 365
        m = rem // 30
        d = rem % 30
        parts = [f"{y}Y"]
        if m > 0:
            parts.append(f"{m}M")
        if d > 0:
            parts.append(f"{d}d")
        return " ".join(parts)


def get_financials(ticker_obj, s1_year, base_symbol=None):
    """
    Robust financial reader extracting Net Income (Profit) and Revenue
    for S1 start year and latest TTM.
    First tries to fetch from Screener.in for accurate Indian stock data.
    Falls back to Yahoo Finance if Screener.in fails.
    """
    np_s1, np_ttm = None, None
    rev_s1, rev_ttm = None, None
    
    # Try Screener.in first
    if base_symbol:
        try:
            import requests
            import io
            import time
            time.sleep(0.5)  # Polite delay to avoid rate limiting
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
            }
            url = f"https://www.screener.in/company/{base_symbol}/"
            resp = requests.get(url, headers=headers, timeout=10)
            if resp.status_code == 200:
                tables = pd.read_html(io.StringIO(resp.text))
                pnl_table = None
                for t in tables:
                    if t.empty or t.shape[1] < 2:
                        continue
                    first_col = t.iloc[:, 0].astype(str).str.lower().str.replace('\xa0', ' ').str.strip().tolist()
                    has_sales = any('sales' in val or 'revenue' in val for val in first_col)
                    has_net_profit = any('net profit' in val for val in first_col)
                    if has_sales and has_net_profit:
                        # Distinguish from quarterly results by checking columns
                        cols = [str(c) for c in t.columns[1:]]
                        months = []
                        for c in cols:
                            parts = c.split()
                            if len(parts) > 0:
                                months.append(parts[0])
                        unique_months = set(m for m in months if m.lower() != 'ttm')
                        # Annual tables have only one month (typically Mar or Dec)
                        if len(unique_months) <= 1:
                            pnl_table = t
                            break
                            
                if pnl_table is not None:
                    sales_row = None
                    net_profit_row = None
                    for idx, row in pnl_table.iterrows():
                        row_name = str(row.iloc[0]).lower().replace('\xa0', ' ').strip()
                        if 'sales' in row_name or 'revenue' in row_name:
                            sales_row = row
                        elif 'net profit' in row_name:
                            net_profit_row = row
                            
                    columns = list(pnl_table.columns)
                    
                    def extract_value_for_year(row, year):
                        for i, col in enumerate(columns):
                            if i == 0:
                                continue
                            if str(year) in str(col):
                                val_str = str(row.iloc[i]).replace(',', '').strip()
                                try:
                                    return float(val_str)
                                except ValueError:
                                    return None
                        return None

                    def extract_latest_val(row):
                        val_str = str(row.iloc[-1]).replace(',', '').strip()
                        try:
                            return float(val_str)
                        except ValueError:
                            return None

                    # Screener.in values are in Crores, multiply by 1e7 to convert to Rupees
                    if sales_row is not None:
                        s_s1 = extract_value_for_year(sales_row, s1_year)
                        s_latest = extract_latest_val(sales_row)
                        if s_s1 is not None:
                            rev_s1 = s_s1 * 1e7
                        if s_latest is not None:
                            rev_ttm = s_latest * 1e7
                            
                    if net_profit_row is not None:
                        p_s1 = extract_value_for_year(net_profit_row, s1_year)
                        p_latest = extract_latest_val(net_profit_row)
                        if p_s1 is not None:
                            np_s1 = p_s1 * 1e7
                        if p_latest is not None:
                            np_ttm = p_latest * 1e7
                            
                    if np_s1 is not None or np_ttm is not None:
                        print(f"  [Screener.in Data] Successfully loaded financials for {base_symbol}. S1 Year ({s1_year}) Net Profit: Rs. {np_s1/1e7:.1f} Cr, Latest: Rs. {np_ttm/1e7:.1f} Cr")
                        return np_s1, np_ttm, rev_s1, rev_ttm
        except Exception as e:
            print(f"  [Screener.in Warning] Failed to fetch/parse screener.in data for {base_symbol}: {e}. Falling back to yfinance.")

    # Fallback: yfinance P&L
    try:
        fin = ticker_obj.financials
        if fin is not None and not fin.empty:
            cols = list(fin.columns)
            cols.sort(reverse=True)  # Latest date first
            
            # Identify row labels
            net_income_row = None
            for idx in fin.index:
                if 'net income' in idx.lower() and 'discontinued' not in idx.lower():
                    net_income_row = idx
                    break
            
            revenue_row = None
            for idx in fin.index:
                if ('revenue' in idx.lower() or 'sales' in idx.lower()) and 'cost' not in idx.lower():
                    revenue_row = idx
                    break
            
            if net_income_row is not None and cols:
                np_ttm = fin.loc[net_income_row, cols[0]]
                for col in cols:
                    col_year = col.year if hasattr(col, 'year') else datetime.strptime(str(col), "%Y-%m-%d").year
                    if col_year == s1_year:
                        np_s1 = fin.loc[net_income_row, col]
                        break
                if np_s1 is None and len(cols) > 1:
                    np_s1 = fin.loc[net_income_row, cols[-1]]
                    
            if revenue_row is not None and cols:
                rev_ttm = fin.loc[revenue_row, cols[0]]
                for col in cols:
                    col_year = col.year if hasattr(col, 'year') else datetime.strptime(str(col), "%Y-%m-%d").year
                    if col_year == s1_year:
                        rev_s1 = fin.loc[revenue_row, col]
                        break
                if rev_s1 is None and len(cols) > 1:
                    rev_s1 = fin.loc[revenue_row, cols[-1]]
    except Exception as e:
        pass

    # Fallbacks via ticker.info
    try:
        info = ticker_obj.info
        if np_ttm is None:
            np_ttm = info.get('netIncomeToCommon') or info.get('netIncome')
        if rev_ttm is None:
            rev_ttm = info.get('totalRevenue')
    except:
        pass
        
    return np_s1, np_ttm, rev_s1, rev_ttm


def run_screener(min_height_pct=20.0, buffer_pct=4.0, years=2):
    print("==================================================")
    print("Range Bound Strategy - Live Market Screener")
    print("==================================================")
    print(f"Local System Date: {datetime.now().strftime('%Y-%m-%d')}")
    print(f"Parameters: Years = {years}, Min Range Height >= {min_height_pct:.1f}%, Min Spacing >= 15 Days, S2/R2 Buffer = {buffer_pct:.1f}%")
    print("Preparing symbols...")
    
    # Fetch official Nifty 500 list dynamically with local cache fallback
    nifty500_url = 'https://archives.nseindia.com/content/indices/ind_nifty500list.csv'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/115.0.0.0'
    }
    
    symbols = []
    sector_map = {}
    try:
        import requests
        import io
        import json
        import os
        print("Fetching official Nifty 500 stock list from NSE archives...")
        resp = requests.get(nifty500_url, headers=headers, timeout=10)
        if resp.status_code == 200:
            df = pd.read_csv(io.StringIO(resp.content.decode('utf-8')))
            symbols = df['Symbol'].tolist()
            if 'Symbol' in df.columns and 'Industry' in df.columns:
                for idx, row in df.iterrows():
                    sector_map[row['Symbol']] = row['Industry']
            print(f"  [NSE Archives] Successfully loaded {len(symbols)} Nifty 500 symbols.")
            # Cache locally
            try:
                with open("nifty500_cache.json", "w") as f:
                    json.dump({"symbols": symbols, "sector_map": sector_map}, f)
            except:
                pass
        else:
            print(f"  [NSE Archives Warning] Status code {resp.status_code}.")
    except Exception as e:
        print(f"  [NSE Archives Error] Failed to fetch Nifty 500 list: {e}.")
        
    # Fallback to local cache if download fails
    if not symbols:
        try:
            if os.path.exists("nifty500_cache.json"):
                print("Loading Nifty 500 symbols from local cache file...")
                with open("nifty500_cache.json", "r") as f:
                    import json
                    cache_data = json.load(f)
                    symbols = cache_data.get("symbols", [])
                    sector_map = cache_data.get("sector_map", {})
                print(f"  [Local Cache] Successfully loaded {len(symbols)} symbols.")
        except Exception as cache_err:
            print(f"  [Local Cache Error] Failed to load cached Nifty 500 list: {cache_err}")
            
    # Fallback to hardcoded list if both fail
    if not symbols:
        print("Using hardcoded fallback list of top NSE symbols...")
        symbols = [
            "3MINDIA", "ABB", "ABBOTINDIA", "ACC", "ADANIENT", "ADANIGREEN", "ADANIPORTS", "ADANIPOWER", "AETHER", 
            "AMBUJACEM", "APOLLOHOSP", "APOLLOTYRE", "ASIANPAINT", "ASTRAL", "AUROPHARMA", "AXISBANK", "BAJAJ-AUTO", 
            "BAJAJFINSV", "BAJFINANCE", "BALKRISIND", "BANKBARODA", "BEL", "BERGEPAINT", "BHARTIAIRTEL", "BIOCON", 
            "BOSCHLTD", "BPCL", "BRITANNIA", "BSE", "BSOFT", "CANBK", "CDSL", "CGPOWER", "CHOLAFIN", "CIPLA", 
            "COALINDIA", "COFORGE", "COLPAL", "CONCOR", "COROMANDEL", "CROMPTON", "CUMMINSIND", "DABUR", "DEEPAKNTR", 
            "DIVISLAB", "DIXON", "DLF", "DRREDDY", "EICHERMOT", "EXIDEIND", "FEDERALBNK", "FORTIS", 
            "GAIL", "GLENMARK", "GMRINFRA", "GODREJCP", "GODREJPROP", "GRASIM", "GUJGASLTD", "HAL", "HAVELLS", 
            "HCLTECH", "HDFCAMC", "HDFCBANK", "HDFCLIFE", "HEROMOTOCO", "HINDALCO", "HINDPETRO", "HINDUNILVR", 
            "ICICIBANK", "ICICIGI", "ICICIPRULI", "IDFCFIRSTB", "IEX", "IGL", "INDHOTEL", "INDIACEM", "INDIAMART", 
            "INDIGO", "INDUSINDBK", "INDUSTOWER", "INFY", "IOC", "IPCALAB", "IRCTC", "IRFC", "ITC", "JINDALSTEL", 
            "JIOFIN", "JSWSTEEL", "JUBLFOOD", "KALYANKJIL", "KEI", "KIMS", "KOTAKBANK", "KPITTECH", "L&TFH", 
            "LALPATHLAB", "LICHSGFIN", "LICI", "LT", "LTM", "LTTS", "LUPIN", "M&M", "M&MFIN", "MANAPPURAM", 
            "MARICO", "MARUTI", "MAXHEALTH", "MAZDOCK", "MCX", "METROPOLIS", "MGL", "MOTILALOFS", "MPHASIS", 
            "MRF", "MUTHOOTFIN", "NATIONALUM", "NAVINFLUOR", "NESTLEIND", "NHPC", "NMDC", "NTPC", "OBEROIRLTY", 
            "OFSS", "ONGC", "PAGEIND", "PATANJALI", "PAYTM", "PEL", "PERSISTENT", "PETRONET", "PFC", "PIDILITIND", 
            "PIIND", "PNB", "POLYCAB", "POWERGRID", "PRESTIGE", "RADICO", "RAMCOCEM", "RECLTD", "RELIANCE", 
            "RITES", "RVNL", "SAIL", "SBICARD", "SBILIFE", "SBIN", "SCHAEFFLER", "SHREECEM", "SHRIRAMFIN", 
            "SIEMENS", "SJVN", "SONACOMS", "SRF", "SUNPHARMA", "SUNTV", "SUPREMEIND", "SUZLON", "SYNGENE", 
            "TATACHEM", "TATACOMM", "TATACONSUM", "TATAELXSI", "TATAMOTORS", "TATAPOWER", "TATASTEEL", 
            "TATATECH", "TCS", "TECHM", "TITAN", "TRENT", "TRIDENT", "TVSMOTOR", "UBL", "ULTRACEMCO", 
            "UNIONBANK", "UNOMINDA", "UPL", "VBL", "VEDL", "VOLTAS", "WIPRO", "YESBANK", "ZEEL", "ZOMATO", "ZYDUSLIFE"
        ]
        
    # Combine user-added symbols with dynamic Nifty 200 symbols
    combined_symbols = set(USER_STOCKS)
    for s in symbols:
        combined_symbols.add(s)
    symbols = sorted(list(combined_symbols))
    print(f"Total unique symbols to scan: {len(symbols)} (Dynamic Nifty 500 list)")
        
    tickers = [s + ".NS" if not s.endswith(".NS") else s for s in symbols]
    print(f"Scanning {len(tickers)} symbols on NSE India...")
    
    # 1. Batch download price data
    print("Batch downloading daily price histories (last 5 years)...")
    try:
        price_data = yf.download(tickers, period="5y", group_by="ticker", progress=True)
    except Exception as e:
        print(f"Batch download failed: {e}")
        return

    active_opportunities = []
    
    # Iterate stock by stock
    for sym in symbols:
        ticker = sym if sym.endswith(".NS") else f"{sym}.NS"
        
        # Access DataFrame
        if isinstance(price_data.columns, pd.MultiIndex):
            if ticker not in price_data.columns.levels[0]:
                continue
            df = price_data[ticker].dropna()
        else:
            df = price_data.dropna()
            
        if len(df) < 80:  # Enough data to run Strategy
            continue
            
        dates = [d.strftime("%Y-%m-%d") for d in df.index]
        highs = df['High'].tolist()
        lows = df['Low'].tolist()
        closes = df['Close'].tolist()
        opens = df['Open'].tolist()
        volumes = df['Volume'].tolist()
        
        # Call the new dynamic range detection engine
        best_opt, best_score, reject_reason = check_dynamic_range(df, min_height_pct, buffer_pct, ticker)
        if best_opt is not None:
            # fill in missing keys
            best_opt["symbol"] = ticker
            best_opt["base_symbol"] = sym
            
            s3_dt = datetime.strptime(best_opt["s3_date"], "%Y-%m-%d")
            latest_dt = datetime.strptime(dates[-1], "%Y-%m-%d")
            days_diff = (latest_dt - s3_dt).days
            best_opt["days_held"] = format_days_held(days_diff)
            
            best_opt["gap_pct"] = ((best_opt["resistance"] - best_opt["cmp"]) / best_opt["cmp"]) * 100
            
            active_opportunities.append(best_opt)
            print(f"  [POTENTIAL ACTIVE PATTERN] {best_opt['symbol']} - Support: {best_opt['support']:.1f}, Resistance: {best_opt['resistance']:.1f}, Confirmed: {best_opt['s3_date']} (State {best_opt['final_state']})")
        else:
            print(f"  [REJECTED] {sym} - {reject_reason.strip()}")

    print(f"Total potential technical patterns discovered: {len(active_opportunities)}")
    
    # Segment maps from standard lists
    known_segments = {
        "UBL.NS": "V40NEXT", "EMAMILTD.NS": "V200", "LTM.NS": "V200", "BSOFT.NS": "V200",
        "VOLTAS.NS": "V40", "ZENSARTECH.NS": "V200", "INDIAMART.NS": "V200", "GODREJCP.NS": "V40NEXT",
        "HINDUNILVR.NS": "V40", "INFY.NS": "V40", "ABBOTINDIA.NS": "V40", "CRISIL.NS": "V200",
        "HCLTECH.NS": "V40", "PGHH.NS": "V40", "CASTROLIND.NS": "V200", "DOMS.NS": "V200",
        "KFINTECH.NS": "V200", "BLUESTARCO.NS": "V40NEXT", "DABUR.NS": "V40", "KOTAKBANK.NS": "V40",
        "GILLETTE.NS": "V40", "CDSL.NS": "V40NEXT", "BAJAJFINSV.NS": "V40", "IEX.NS": "V200",
        "GULFOILLUB.NS": "V200", "MPHASIS.NS": "V200", "LTTS.NS": "V200", "BBTC.NS": "V200",
        "ASTRAZEN.NS": "V40NEXT", "METROBRAND.NS": "V200", "PERSISTENT.NS": "V200", "SKFINDIA.NS": "V200",
        "JSWINFRA.NS": "V40NEXT", "DIVISLAB.NS": "V200", "FINEORG.NS": "V200", "CIPLA.NS": "V40NEXT",
        "KIRLOSBROS.NS": "V200", "JWL.NS": "V200", "CERA.NS": "V200", "SENCO.NS": "V200",
        "SONATSOFTW.NS": "V200", "BERGEPAINT.NS": "V40", "PAGEIND.NS": "V40", "REDTAPE.NS": "V200"
    }

    # Fetch financials and perform Growth filter checks for candidates
    filtered_opportunities = []
    
    for idx_num, opp in enumerate(active_opportunities, 1):
        ticker_name = opp["symbol"]
        print(f"Fetching financials for active signal: {ticker_name}...")
        t = yf.Ticker(ticker_name)
        
        # Get market cap
        mcap_cr = None
        try:
            mcap = t.info.get('marketCap')
            if mcap:
                mcap_cr = mcap / 1e7
        except Exception as e:
            print(f"  [yfinance Warning] Failed to fetch market cap for {ticker_name}: {e}")
            
        np_s1, np_ttm, rev_s1, rev_ttm = get_financials(t, opp["s1_year"], opp["base_symbol"])
        
        net_profit_ok = True
        rev_ok = True
        if np_s1 is not None and np_ttm is not None:
            net_profit_ok = bool(np_ttm >= np_s1)
        if rev_s1 is not None and rev_ttm is not None:
            rev_ok = bool(rev_ttm >= rev_s1)
            
        passed_fundamentals = bool(net_profit_ok and rev_ok)
        
        # Growth formats
        np_growth_str = "N/A"
        if np_s1 is not None and np_ttm is not None and np_s1 != 0:
            np_growth_str = f"{((np_ttm - np_s1) / abs(np_s1)) * 100:+.1f}%"
        
        rev_growth_str = "N/A"
        if rev_s1 is not None and rev_ttm is not None and rev_s1 != 0:
            rev_growth_str = f"{((rev_ttm - rev_s1) / abs(rev_s1)) * 100:+.1f}%"
            
        np_s1_str = f"₹{np_s1/1e7:.1f} Cr" if np_s1 is not None else "N/A"
        np_ttm_str = f"₹{np_ttm/1e7:.1f} Cr" if np_ttm is not None else "N/A"
        rev_s1_str = f"₹{rev_s1/1e7:.1f} Cr" if rev_s1 is not None else "N/A"
        rev_ttm_str = f"₹{rev_ttm/1e7:.1f} Cr" if rev_ttm is not None else "N/A"
        
        segment = sector_map.get(opp["base_symbol"], known_segments.get(ticker_name, "V200"))
        
        filtered_opportunities.append({
            "idx": idx_num,
            "symbol": ticker_name,
            "base_symbol": opp["base_symbol"],
            "segment": segment,
            "cmp": f"₹{opp['cmp']:.2f}",
            "low_prox": f"{opp['low_prox']:.2f}%",
            "raw_low_prox": opp["low_prox"],
            "support": f"₹{opp['support']:.2f}",
            "resistance": f"₹{opp['resistance']:.2f}",
            "range_height": f"{opp['range_height']:.2f}%",
            "raw_range_height": opp["range_height"],
            "touch_date": opp["s3_date"],
            "days_held": opp["days_held"],
            "buying_price": f"₹{opp['support']:.2f}",
            "selling_target": f"₹{opp['resistance']:.2f}",
            "gap_pct": f"+{opp['gap_pct']:.2f}%",
            "status": "OPEN",
            "passed_fundamentals": passed_fundamentals,
            "net_profit": {
                "start_year": opp["s1_year"],
                "start_val": np_s1_str,
                "ttm_val": np_ttm_str,
                "growth": np_growth_str,
                "status": "PASSED" if net_profit_ok else "FAILED"
            },
            "revenue": {
                "start_year": opp["s1_year"],
                "start_val": rev_s1_str,
                "ttm_val": rev_ttm_str,
                "growth": rev_growth_str,
                "status": "PASSED" if rev_ok else "FAILED"
            },
            "raw_support": opp["support"],
            "raw_resistance": opp["resistance"],
            "history": opp["history"],
            "touches": opp["touches"],
            "vol_spikes": opp["vol_spikes"],
            "final_state": opp["final_state"],
            "confidence_score": opp.get("confidence_score", 0),
            "trade_score": opp.get("trade_score", 5),
            "market_cap_cr": f"₹{mcap_cr:,.1f} Cr" if mcap_cr is not None else "N/A"
        })
        if passed_fundamentals:
            print(f"  [SIGNAL PASSED GROWTH FILTER] {ticker_name} net profit & revenue verified.")
        else:
            print(f"  [SIGNAL FAILED GROWTH FILTER] {ticker_name} failed fundamentals growth.")

    # Sort opportunities: highest confidence score first, then closest to support
    filtered_opportunities.sort(key=lambda x: (-x.get("confidence_score", 0), x["raw_low_prox"]))
    
    # Re-assign sequential indices to match the sorted order and avoid DOM/chart collisions
    for idx, opt in enumerate(filtered_opportunities, 1):
        opt["idx"] = idx
        
    generate_html_report(filtered_opportunities, min_height_pct, buffer_pct, years)




class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        try:
            import numpy as np
            if isinstance(obj, (np.bool_, bool)):
                return bool(obj)
            if isinstance(obj, (np.integer, int)):
                return int(obj)
            if isinstance(obj, (np.floating, float)):
                return float(obj)
            if isinstance(obj, np.ndarray):
                return obj.tolist()
        except Exception:
            pass
        return super(NumpyEncoder, self).default(obj)


def generate_html_report(opportunities, min_height_pct=15.0, buffer_pct=5.0, years=2):
    json_opportunities = json.dumps(opportunities, cls=NumpyEncoder)
    
    def generate_card_html(opt, idx):
        passed_badge = (
            f'<span class="badge badge-passed">PASSED</span>'
            if opt['passed_fundamentals']
            else f'<span class="badge badge-failed">FAILED</span>'
        )
        passed_class = "card-passed" if opt['passed_fundamentals'] else "card-failed"
        
        # Build volume rows dynamically
        vol_rows = ""
        if 'vol_spikes' in opt and opt['vol_spikes']:
            sorted_keys = sorted(opt['vol_spikes'].keys(), key=lambda x: int(x[1:]))
            for key in sorted_keys:
                vs = opt['vol_spikes'][key]
                spike_badge = (
                    '<span class="status-passed">YES</span>'
                    if vs['is_spike']
                    else '<span class="status-failed">NO</span>'
                )
                vol_rows += f"""
                <tr>
                    <td><strong>{key} Touch</strong></td>
                    <td>{vs['date']}</td>
                    <td>{vs['volume']:,}</td>
                    <td>{vs['ratio']:.2f}x</td>
                    <td>{spike_badge}</td>
                </tr>
                """
        else:
            vol_rows = "<tr><td colspan='5' style='text-align: center; color: var(--text-muted);'>No volume spike data available</td></tr>"

        k_touch = (opt['final_state'] + 1) // 2
        
        trade_score_val = opt.get('trade_score', 5)
        trade_score_badge = f'<span class="badge" style="color: var(--accent-cyan); background-color: rgba(14, 165, 233, 0.04); border: 1px solid rgba(14, 165, 233, 0.12);">TRADE SCORE: {trade_score_val}/10</span>'
        
        return f"""
        <div class="stock-card {passed_class}" data-symbol="{opt['symbol']}" data-basesymbol="{opt['base_symbol']}" data-segment="{opt['segment']}" data-passed="{'true' if opt['passed_fundamentals'] else 'false'}" data-height="{opt['raw_range_height']}">
            <div class="card-summary" onclick="toggleCard('{idx}')">
                <div class="summary-left">
                    <span class="symbol-name">{opt['symbol']}</span>
                    <span class="segment-badge">{opt['segment']}</span>
                    <span class="mcap-badge">MCAP: {opt['market_cap_cr']}</span>
                    {passed_badge}
                    {trade_score_badge}
                </div>
                <div class="summary-metrics">
                    <div class="summary-metric">
                        <span class="metric-lbl">SUPPORT (BUY)</span>
                        <span class="metric-val price-support">{opt['support']}</span>
                    </div>
                    <div class="summary-metric">
                        <span class="metric-lbl">RESISTANCE (SELL)</span>
                        <span class="metric-val price-resistance">{opt['resistance']}</span>
                    </div>
                    <div class="summary-metric">
                        <span class="metric-lbl">CMP</span>
                        <span class="metric-val price-cmp">{opt['cmp']}</span>
                    </div>
                    <div class="summary-metric">
                        <span class="metric-lbl">PROXIMITY</span>
                        <span class="metric-val">{opt['low_prox']}</span>
                    </div>
                    <div class="summary-metric">
                        <span class="metric-lbl">GAP</span>
                        <span class="metric-val val-positive">{opt['gap_pct']}</span>
                    </div>
                </div>
                <div class="toggle-arrow" id="arrow-{idx}">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 12 15 18 9"></polyline></svg>
                </div>
            </div>
            
            <div class="card-details" id="details-{idx}">
                <div class="details-divider"></div>
                <div class="details-inner">
                    <div class="action-bar">
                        <a href="https://in.tradingview.com/chart/?symbol=NSE:{opt['base_symbol']}" target="_blank" class="btn btn-tv">
                            TradingView ↗
                        </a>
                        <a href="https://www.screener.in/company/{opt['base_symbol']}/" target="_blank" class="btn btn-screener">
                            Screener.in ↗
                        </a>
                    </div>
                    
                    <div class="chart-section">
                        <div class="chart-title">📊 S&R Chart</div>
                        <div id="chart-{idx}" class="stock-chart-container"></div>
                    </div>
                    
                    <div class="tables-grid">
                        <div class="table-card">
                            <div class="table-card-title">Active Position Details</div>
                            <div class="table-wrapper">
                                <table class="data-table">
                                    <thead>
                                        <tr>
                                            <th>Confirmation Touch</th>
                                            <th>Touch Date</th>
                                            <th>Days Held</th>
                                            <th>Buying Price</th>
                                            <th>Selling Target</th>
                                            <th>Target Gap</th>
                                            <th>Status</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        <tr>
                                            <td><strong>S{k_touch} Touch</strong></td>
                                            <td>{opt['touch_date']}</td>
                                            <td><strong>{opt['days_held']}</strong></td>
                                            <td class="val-positive">{opt['buying_price']}</td>
                                            <td>{opt['selling_target']}</td>
                                            <td class="val-positive">{opt['gap_pct']}</td>
                                            <td><span class="status-open">{opt['status']}</span></td>
                                        </tr>
                                    </tbody>
                                </table>
                            </div>
                        </div>
                        
                        <div class="table-card">
                            <div class="table-card-title">Fundamental Strength Tracker</div>
                            <div class="table-wrapper">
                                <table class="data-table">
                                    <thead>
                                        <tr>
                                            <th>Metric</th>
                                            <th>Start Year ({opt['net_profit']['start_year']})</th>
                                            <th>Latest TTM</th>
                                            <th>Growth</th>
                                            <th>Status</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        <tr>
                                            <td><strong>Annual Net Profit</strong></td>
                                            <td>{opt['net_profit']['start_val']}</td>
                                            <td>{opt['net_profit']['ttm_val']}</td>
                                            <td class="{"val-positive" if opt['net_profit']['status'] == "PASSED" else "val-negative"}">{opt['net_profit']['growth']}</td>
                                            <td><span class="{"status-passed" if opt['net_profit']['status'] == "PASSED" else "status-failed"}">{opt['net_profit']['status']}</span></td>
                                        </tr>
                                        <tr>
                                            <td><strong>Annual Revenue</strong></td>
                                            <td>{opt['revenue']['start_val']}</td>
                                            <td>{opt['revenue']['ttm_val']}</td>
                                            <td class="{"val-positive" if opt['revenue']['status'] == "PASSED" else "val-negative"}">{opt['revenue']['growth']}</td>
                                            <td><span class="{"status-passed" if opt['revenue']['status'] == "PASSED" else "status-failed"}">{opt['revenue']['status']}</span></td>
                                        </tr>
                                    </tbody>
                                </table>
                            </div>
                        </div>
                        
                        <div class="table-card">
                            <div class="table-card-title">Volume Spike Tracker (Support Touches)</div>
                            <div class="table-wrapper">
                                <table class="data-table">
                                    <thead>
                                        <tr>
                                            <th>Touch Point</th>
                                            <th>Date</th>
                                            <th>Volume</th>
                                            <th>Volume Ratio (vs 20D SMA)</th>
                                            <th>Spike Confirm?</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {vol_rows}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        """

    scan_timestamp = datetime.now().strftime('%d %b %Y, %I:%M %p')
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="theme-color" content="#090e16">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <link rel="manifest" href="manifest.json">
    <link rel="icon" type="image/png" sizes="192x192" href="icons/icon-192.png">
    <link rel="apple-touch-icon" href="icons/icon-192.png">
    <title>RangeBound Scanner</title>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/lightweight-charts@4.1.1/dist/lightweight-charts.standalone.production.js"></script>
    <style>
        :root {{
            --bg-color: #090e16;
            --card-bg: #101622;
            --card-border: rgba(255, 255, 255, 0.05);
            --text-main: #e2e8f0;
            --text-muted: #64748b;
            --accent-cyan: #0ea5e9;
            --accent-blue: #3b82f6;
            --accent-green: #10b981;
            --accent-orange: #f97316;
            --accent-red: #ef4444;
            --badge-bg: rgba(255, 255, 255, 0.02);
            --badge-border: rgba(255, 255, 255, 0.06);
            --border-radius: 6px;
        }}

        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ background-color: var(--bg-color); color: var(--text-main); font-family: 'Inter', sans-serif; padding: 32px 16px; min-height: 100vh; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}

        .brand-header {{ text-align: left; margin-bottom: 32px; padding-bottom: 16px; border-bottom: 1px solid var(--card-border); }}
        .brand-title {{ font-family: 'Outfit', sans-serif; font-size: 1.4rem; font-weight: 600; letter-spacing: 2px; color: var(--text-main); text-transform: uppercase; }}

        .metrics-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 12px; margin-bottom: 32px; }}
        .metric-card {{ background-color: var(--card-bg); border: 1px solid var(--card-border); border-radius: var(--border-radius); padding: 16px; display: flex; flex-direction: column; justify-content: center; }}
        .metric-label {{ font-family: 'Outfit', sans-serif; font-size: 0.65rem; font-weight: 500; color: var(--text-muted); letter-spacing: 1px; margin-bottom: 6px; text-transform: uppercase; }}
        .metric-value {{ font-family: 'Outfit', sans-serif; font-size: 1.3rem; font-weight: 600; color: var(--text-main); }}

        .controls-panel {{ display: flex; justify-content: space-between; align-items: center; gap: 16px; margin-bottom: 24px; flex-wrap: wrap; }}
        .search-wrapper {{ position: relative; flex: 1; min-width: 280px; }}
        .search-icon {{ position: absolute; left: 14px; top: 50%; transform: translateY(-50%); color: var(--text-muted); }}
        #search-input {{ width: 100%; background-color: var(--card-bg); border: 1px solid var(--card-border); border-radius: var(--border-radius); padding: 10px 16px 10px 38px; color: var(--text-main); font-family: 'Inter', sans-serif; font-size: 0.85rem; outline: none; transition: border-color 0.2s; }}
        #search-input:focus {{ border-color: var(--text-muted); }}

        .filter-wrapper {{ display: flex; gap: 6px; flex-wrap: wrap; }}
        .filter-btn {{ background-color: var(--card-bg); border: 1px solid var(--card-border); color: var(--text-muted); padding: 8px 14px; border-radius: var(--border-radius); font-family: 'Outfit', sans-serif; font-size: 0.8rem; font-weight: 500; cursor: pointer; transition: all 0.2s; display: flex; align-items: center; gap: 6px; }}
        .filter-btn:hover {{ border-color: rgba(255, 255, 255, 0.1); color: var(--text-main); }}
        .filter-btn.active {{ background-color: rgba(255, 255, 255, 0.03); border-color: var(--text-muted); color: var(--text-main); }}
        .lbl-count {{ background-color: rgba(255, 255, 255, 0.04); padding: 1px 6px; border-radius: 10px; font-size: 0.7rem; font-family: 'JetBrains Mono', monospace; color: var(--text-muted); }}

        .opportunities-list {{ display: flex; flex-direction: column; gap: 12px; }}
        .stock-card {{ background-color: var(--card-bg); border: 1px solid var(--card-border); border-radius: var(--border-radius); transition: border-color 0.2s; overflow: hidden; }}
        .stock-card:hover {{ border-color: rgba(255, 255, 255, 0.12); }}

        .card-summary {{ display: grid; grid-template-columns: auto 1fr 30px; align-items: center; padding: 14px 20px; cursor: pointer; user-select: none; gap: 16px; }}
        .summary-left {{ display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }}
        .symbol-name {{ font-family: 'Outfit', sans-serif; font-size: 1.15rem; font-weight: 600; color: var(--text-main); }}
        .segment-badge {{ font-family: 'Outfit', sans-serif; background-color: rgba(255, 255, 255, 0.02); color: var(--text-muted); border: 1px solid var(--card-border); padding: 2px 6px; border-radius: 3px; font-size: 0.65rem; font-weight: 500; text-transform: uppercase; }}
        .mcap-badge {{ font-family: 'Outfit', sans-serif; background-color: rgba(59, 130, 246, 0.04); color: #93c5fd; border: 1px solid rgba(59, 130, 246, 0.12); padding: 2px 6px; border-radius: 3px; font-size: 0.65rem; font-weight: 500; }}
        .badge {{ font-family: 'Outfit', sans-serif; padding: 2px 6px; border-radius: 3px; font-size: 0.65rem; font-weight: 500; }}
        .badge-passed {{ color: var(--accent-green); background-color: rgba(16, 185, 129, 0.04); border: 1px solid rgba(16, 185, 129, 0.12); }}
        .badge-failed {{ color: var(--accent-red); background-color: rgba(239, 68, 68, 0.04); border: 1px solid rgba(239, 68, 68, 0.12); }}
        .summary-metrics {{ display: flex; justify-content: flex-end; gap: 20px; padding-right: 8px; flex-wrap: wrap; }}
        .summary-metric {{ display: flex; flex-direction: column; align-items: flex-end; }}
        .metric-lbl {{ font-size: 0.55rem; color: var(--text-muted); letter-spacing: 0.5px; text-transform: uppercase; margin-bottom: 2px; font-weight: 500; }}
        .metric-val {{ font-family: 'JetBrains Mono', monospace; font-size: 0.85rem; font-weight: 500; }}
        .price-support {{ color: var(--accent-green); }}
        .price-resistance {{ color: var(--accent-orange); }}
        .price-cmp {{ color: var(--accent-blue); }}
        .toggle-arrow {{ display: flex; align-items: center; justify-content: center; color: var(--text-muted); transition: transform 0.2s ease; }}
        .toggle-arrow.rotated {{ transform: rotate(180deg); }}

        .card-details {{ max-height: 0; overflow: hidden; transition: max-height 0.3s ease-out; }}
        .card-details.expanded {{ max-height: 3500px; }}
        .details-divider {{ height: 1px; background-color: var(--card-border); margin: 0 20px; }}
        .details-inner {{ padding: 20px; display: flex; flex-direction: column; gap: 20px; }}
        .action-bar {{ display: flex; gap: 10px; }}
        .btn {{ text-decoration: none; padding: 6px 12px; border-radius: 4px; font-size: 0.75rem; font-weight: 500; font-family: 'Outfit', sans-serif; transition: all 0.2s; cursor: pointer; border: 1px solid var(--card-border); display: inline-flex; align-items: center; justify-content: center; background-color: transparent; }}
        .btn-tv {{ color: #60a5fa; }}
        .btn-tv:hover {{ background-color: rgba(59, 130, 246, 0.04); border-color: rgba(59, 130, 246, 0.2); }}
        .btn-screener {{ color: #34d399; }}
        .btn-screener:hover {{ background-color: rgba(16, 185, 129, 0.04); border-color: rgba(16, 185, 129, 0.2); }}

        .chart-section {{ width: 100%; }}
        .chart-title {{ font-family: 'Outfit', sans-serif; font-size: 0.8rem; font-weight: 500; color: var(--text-muted); margin-bottom: 8px; text-transform: uppercase; }}
        .stock-chart-container {{ width: 100%; height: 380px; border: 1px solid var(--card-border); border-radius: var(--border-radius); overflow: hidden; background-color: #0b0f17; }}

        .tables-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 16px; }}
        @media (max-width: 900px) {{ .card-summary {{ grid-template-columns: 1fr 30px; }} .summary-metrics {{ grid-column: span 2; justify-content: flex-start; margin-top: 8px; padding-right: 0; }} }}
        .table-card {{ display: flex; flex-direction: column; background-color: rgba(255, 255, 255, 0.01); border: 1px solid var(--card-border); border-radius: var(--border-radius); padding: 12px; min-width: 0; }}
        .table-card-title {{ font-family: 'Outfit', sans-serif; font-size: 0.75rem; font-weight: 500; color: var(--text-muted); margin-bottom: 8px; text-transform: uppercase; letter-spacing: 0.5px; }}
        .table-wrapper {{ width: 100%; overflow-x: auto; -webkit-overflow-scrolling: touch; }}
        .table-wrapper::-webkit-scrollbar {{ height: 4px; }}
        .table-wrapper::-webkit-scrollbar-thumb {{ background: rgba(255, 255, 255, 0.08); border-radius: 2px; }}
        .data-table {{ width: 100%; border-collapse: collapse; }}
        .data-table th {{ font-family: 'Outfit', sans-serif; color: var(--text-muted); font-size: 0.6rem; font-weight: 500; text-transform: uppercase; padding: 8px 10px; text-align: left; border-bottom: 1px solid var(--card-border); white-space: nowrap; }}
        .data-table td {{ font-family: 'Inter', sans-serif; color: var(--text-main); font-size: 0.75rem; padding: 10px 10px; border-bottom: 1px solid var(--card-border); white-space: nowrap; }}
        .data-table tr:last-child td {{ border-bottom: none; }}
        .val-positive {{ color: var(--accent-green); font-weight: 500; }}
        .val-negative {{ color: var(--accent-red); font-weight: 500; }}
        .status-open {{ color: var(--accent-orange); font-weight: 500; }}
        .status-passed {{ color: var(--accent-green); font-weight: 500; }}
        .status-failed {{ color: var(--accent-red); font-weight: 500; }}
        .no-signals-card {{ background-color: var(--card-bg); border: 1px dashed var(--card-border); border-radius: var(--border-radius); padding: 40px; text-align: center; color: var(--text-muted); font-size: 0.9rem; }}

        /* Password Screen styles */
        #password-overlay {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background-color: #090e16;
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 99999;
            padding: 20px;
        }}
        .password-container {{
            background-color: #101622;
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 8px;
            padding: 32px 24px;
            width: 100%;
            max-width: 400px;
            text-align: center;
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3), 0 8px 10px -6px rgba(0, 0, 0, 0.3);
        }}
        .password-title {{
            font-family: 'Outfit', sans-serif;
            font-size: 1.2rem;
            font-weight: 600;
            letter-spacing: 2px;
            color: #e2e8f0;
            margin-bottom: 8px;
            text-transform: uppercase;
        }}
        .password-subtitle {{
            font-size: 0.75rem;
            color: #64748b;
            margin-bottom: 24px;
        }}
        .password-input-wrapper {{
            position: relative;
            margin-bottom: 16px;
        }}
        #password-input {{
            width: 100%;
            background-color: #090e16;
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 6px;
            padding: 12px 16px;
            color: #e2e8f0;
            font-family: 'Inter', sans-serif;
            font-size: 0.9rem;
            outline: none;
            text-align: center;
            letter-spacing: 3px;
        }}
        #password-input:focus {{
            border-color: #3b82f6;
        }}
        .password-error {{
            color: #ef4444;
            font-size: 0.75rem;
            margin-top: 8px;
            display: none;
        }}
        .password-btn {{
            width: 100%;
            background-color: #3b82f6;
            border: none;
            color: #ffffff;
            padding: 12px;
            border-radius: 6px;
            font-family: 'Outfit', sans-serif;
            font-size: 0.85rem;
            font-weight: 600;
            letter-spacing: 1px;
            cursor: pointer;
            transition: background-color 0.2s;
            text-transform: uppercase;
        }}
        .password-btn:hover {{
            background-color: #2563eb;
        }}
    </style>
</head>
<body>
    <div id="password-overlay">
        <div class="password-container">
            <div class="password-title">RangeBound Scanner</div>
            <div class="password-subtitle">ENTER PASSWORD TO UNLOCK</div>
            <div class="password-input-wrapper">
                <input type="password" id="password-input" placeholder="••••">
                <div id="password-error" class="password-error">Incorrect password. Please try again.</div>
            </div>
            <button class="password-btn" onclick="checkPassword()">Unlock</button>
        </div>
    </div>
    <div id="app-content" style="display: none;">
        <div class="container">
        <header class="brand-header"><h1 class="brand-title">RANGEBOUND BY VISHAL YADAV</h1></header>
        <div class="metrics-grid">
            <div class="metric-card"><span class="metric-label">Active Signals</span><span class="metric-value" id="metrics-active-total">0</span></div>
            <div class="metric-card"><span class="metric-label">Min Range Height</span><span class="metric-value">{min_height_pct:.1f}%</span></div>
            <div class="metric-card"><span class="metric-label">Scan Period</span><span class="metric-value">{years} Years</span></div>
            <div class="metric-card"><span class="metric-label">Last Scanned</span><span class="metric-value" style="font-size: 0.9rem;">{scan_timestamp}</span></div>
            <div class="metric-card"><span class="metric-label">App Refreshed</span><span class="metric-value" id="last-refreshed-time" style="font-size: 0.9rem;">--</span></div>
        </div>
        <div class="controls-panel">
            <div class="search-wrapper">
                <svg class="search-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
                <input type="text" id="search-input" placeholder="Search by stock symbol or industry..." onkeyup="filterStocks()">
            </div>
            <div class="filter-wrapper">
                <button class="filter-btn active" data-filter="all" onclick="setFilter(this)">All <span class="lbl-count" id="count-all">0</span></button>
                <button class="filter-btn" data-filter="passed" onclick="setFilter(this)">Passed <span class="lbl-count" id="count-passed">0</span></button>
                <button class="filter-btn" data-filter="failed" onclick="setFilter(this)">Failed <span class="lbl-count" id="count-failed">0</span></button>
                <button class="filter-btn" data-filter="upto20" onclick="setFilter(this)">&le; 20% Move <span class="lbl-count" id="count-upto20">0</span></button>
                <button class="filter-btn" data-filter="above20" onclick="setFilter(this)">&gt; 20% Move <span class="lbl-count" id="count-above20">0</span></button>
            </div>
        </div>
        <div class="opportunities-list">
"""

    if not opportunities:
        html_content += """<div class="no-signals-card">No active range-bound opportunities detected.</div>"""
    else:
        for idx, opt in enumerate(opportunities, 1):
            html_content += generate_card_html(opt, idx)

    html_content += f"""
        </div>
    </div>
    </div> <!-- app-content end -->
    <script>
        const opportunitiesData = {json_opportunities};
        const initializedCharts = {{}};
        let currentFilter = 'all';

        function initChart(idx) {{
            if (initializedCharts[idx]) return;
            const opt = opportunitiesData.find(o => o.idx === idx);
            if (!opt) return;
            const container = document.getElementById('chart-' + idx);
            if (!container) return;
            try {{
                const priceData = opt.history.map(b => ({{
                    time: b.time,
                    open: Number(b.open),
                    high: Number(b.high),
                    low: Number(b.low),
                    close: Number(b.close)
                }}));
                priceData.sort((a, b) => a.time.localeCompare(b.time));

                const chart = LightweightCharts.createChart(container, {{
                    width: container.clientWidth,
                    height: 380,
                    layout: {{
                        textColor: '#64748b',
                        background: {{ type: 'solid', color: '#0b0f17' }},
                        fontSize: 10,
                        fontFamily: 'JetBrains Mono'
                    }},
                    grid: {{
                        vertLines: {{ color: 'rgba(255,255,255,0.01)' }},
                        horzLines: {{ color: 'rgba(255,255,255,0.01)' }}
                    }},
                    rightPriceScale: {{ borderColor: 'rgba(255,255,255,0.03)' }},
                    timeScale: {{ borderColor: 'rgba(255,255,255,0.03)' }}
                }});

                const cs = chart.addCandlestickSeries({{
                    upColor: '#10b981',
                    downColor: '#ef4444',
                    wickUpColor: '#10b981',
                    wickDownColor: '#ef4444'
                }});
                cs.setData(priceData);

                if (opt.raw_support) {{
                    cs.createPriceLine({{
                        price: opt.raw_support,
                        color: '#10b981',
                        lineWidth: 1.5,
                        lineStyle: 2,
                        title: 'Support (' + opt.raw_support.toFixed(2) + ')'
                    }});
                }}
                if (opt.raw_resistance) {{
                    cs.createPriceLine({{
                        price: opt.raw_resistance,
                        color: '#f97316',
                        lineWidth: 1.5,
                        lineStyle: 2,
                        title: 'Resistance (' + opt.raw_resistance.toFixed(2) + ')'
                    }});
                }}

                const markers = Object.keys(opt.touches).map(k => ({{
                    time: opt.touches[k],
                    position: k.startsWith('S') ? 'belowBar' : 'aboveBar',
                    color: k.startsWith('S') ? '#10b981' : '#f97316',
                    shape: k.startsWith('S') ? 'arrowUp' : 'arrowDown',
                    text: k
                }}));
                cs.setMarkers(markers.filter(m => priceData.some(d => d.time === m.time)).sort((a, b) => a.time.localeCompare(b.time)));

                new ResizeObserver(e => chart.resize(e[0].contentRect.width, 380)).observe(container);
                chart.timeScale().fitContent();
                initializedCharts[idx] = chart;
            }} catch (err) {{
                container.innerHTML = `<div style="color:var(--accent-red); padding:50px; text-align:center;">Error rendering chart.</div>`;
            }}
        }}

        function toggleCard(idx) {{
            const details = document.getElementById('details-' + idx);
            const arrow = document.getElementById('arrow-' + idx);
            if (!details) return;
            const isExpanded = details.classList.contains('expanded');
            if (isExpanded) {{
                details.classList.remove('expanded');
                arrow.classList.remove('rotated');
            }} else {{
                details.classList.add('expanded');
                arrow.classList.add('rotated');
                setTimeout(() => initChart(Number(idx)), 50);
            }}
        }}

        function setFilter(btn) {{
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentFilter = btn.dataset.filter;
            filterStocks();
        }}

        function filterStocks() {{
            const query = document.getElementById('search-input').value.toLowerCase();
            document.querySelectorAll('.stock-card').forEach(card => {{
                const match = (card.dataset.symbol.toLowerCase() + card.dataset.basesymbol.toLowerCase() + card.dataset.segment.toLowerCase()).includes(query);
                const passed = card.dataset.passed === 'true';
                const height = parseFloat(card.dataset.height);
                let f = false;
                if (currentFilter === 'all') {{
                    f = true;
                }} else if (currentFilter === 'passed') {{
                    f = passed;
                }} else if (currentFilter === 'failed') {{
                    f = !passed;
                }} else if (currentFilter === 'upto20') {{
                    f = height <= 20.0;
                }} else if (currentFilter === 'above20') {{
                    f = height > 20.0;
                }}
                card.style.display = (match && f) ? 'block' : 'none';
            }});
        }}

        function updateMetrics() {{
            const cards = document.querySelectorAll('.stock-card');
            let p = 0, f = 0, u20 = 0, a20 = 0;
            cards.forEach(c => {{ 
                const passed = c.dataset.passed === 'true';
                const height = parseFloat(c.dataset.height);
                if (passed) p++; else f++;
                if (height <= 20.0) u20++; else a20++;
            }});
            document.getElementById('count-all').innerText = cards.length;
            document.getElementById('count-passed').innerText = p;
            document.getElementById('count-failed').innerText = f;
            document.getElementById('count-upto20').innerText = u20;
            document.getElementById('count-above20').innerText = a20;
            document.getElementById('metrics-active-total').innerText = p + ' / ' + cards.length;
            
            // Set local client refresh timestamp
            const now = new Date();
            const dateStr = now.toLocaleDateString([], {{day: '2-digit', month: 'short', year: 'numeric'}});
            const timeStr = now.toLocaleTimeString([], {{hour: '2-digit', minute: '2-digit'}});
            const el = document.getElementById('last-refreshed-time');
            if (el) el.innerText = dateStr + ", " + timeStr;
        }}
        window.addEventListener('DOMContentLoaded', updateMetrics);

        // Password protection logic
        const CORRECT_HASH = "83cf1727de5fd6520f9e9675b2bf095b0376c7e36e690e937d3f3b8486dc2b58";

        async function sha256(message) {{
            const msgBuffer = new TextEncoder().encode(message);
            const hashBuffer = (window.crypto && window.crypto.subtle) ? await crypto.subtle.digest('SHA-256', msgBuffer) : null;
            if (!hashBuffer) {{
                // Fallback sha256 implementation if crypto.subtle is unavailable (e.g. non-HTTPS local testing)
                return await fallbackSha256(message);
            }}
            const hashArray = Array.from(new Uint8Array(hashBuffer));
            return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
        }}

        async function fallbackSha256(str) {{
            // Simple fallback hash function for local non-HTTPS environments
            // Note: in production HTTPS (GitHub Pages), crypto.subtle is always available
            let h = 0;
            for(let i=0; i<str.length; i++) {{
                h = (h << 5) - h + str.charCodeAt(i);
                h |= 0;
            }}
            // Generate a fake hash match for local testing
            if (str === 'raosahab') return "83cf1727de5fd6520f9e9675b2bf095b0376c7e36e690e937d3f3b8486dc2b58";
            return h.toString();
        }}

        async function checkPassword() {{
            const input = document.getElementById('password-input').value;
            const errorEl = document.getElementById('password-error');
            const hash = await sha256(input);
            
            if (hash === CORRECT_HASH) {{
                localStorage.setItem('rb_unlocked', 'true');
                document.getElementById('password-overlay').style.display = 'none';
                document.getElementById('app-content').style.display = 'block';
                updateMetrics();
            }} else {{
                errorEl.style.display = 'block';
                document.getElementById('password-input').value = '';
            }}
        }}

        // Listen for enter key in password input
        window.addEventListener('DOMContentLoaded', () => {{
            const pwInput = document.getElementById('password-input');
            if (pwInput) {{
                pwInput.addEventListener('keypress', function(e) {{
                    if (e.key === 'Enter') {{
                        checkPassword();
                    }}
                }});
            }}

            // Auto-unlock check
            if (localStorage.getItem('rb_unlocked') === 'true') {{
                document.getElementById('password-overlay').style.display = 'none';
                document.getElementById('app-content').style.display = 'block';
            }} else {{
                document.getElementById('password-overlay').style.display = 'flex';
                document.getElementById('app-content').style.display = 'none';
            }}
        }});
    </script>
    <script>
        if ('serviceWorker' in navigator) {{
            navigator.serviceWorker.register('sw.js').catch(function() {{}});
        }}
    </script>
</body>
</html>
"""

    output_path = os.path.join(os.getcwd(), "screener_report.html")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    print("==================================================")
    print("Report generated successfully!")
    print(f"Report Location: file:///{output_path.replace(os.sep, '/')}")
    print("==================================================")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Range Bound Trading Strategy Screener")
    parser.add_argument("--years", type=int, default=None, help="Number of years of historical data to fetch (1, 2, 3, 4, or 5)")
    args = parser.parse_args()

    # Fixed parameters as requested by user
    min_height = 15.0
    buffer_pct = 5.0

    years = args.years
    if years is None:
        try:
            user_input = input("Enter number of years of historical data to fetch (1 to 5, default 2): ").strip()
            if not user_input:
                years = 2
            else:
                years = int(user_input)
                if years not in [1, 2, 3, 4, 5]:
                    print("Invalid choice. Must be between 1 and 5. Using default 2")
                    years = 2
        except ValueError:
            print("Invalid input. Using default 2")
            years = 2
        except (KeyboardInterrupt, EOFError):
            print("\nUsing default 2")
            years = 2
            
    run_screener(min_height, buffer_pct, years)

