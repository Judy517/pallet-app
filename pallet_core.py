#!/usr/bin/env python
# coding: utf-8

# In[1]:


# -*- coding: utf-8 -*-
import math
from dataclasses import dataclass
from typing import Dict, List, Tuple

# ---------------- Pallet spec ----------------
PALLET_L, PALLET_W, PALLET_H = 48.0, 46.0, 60.0  # inches

@dataclass
class Case:
    L: float; W: float; H: float  # inches

# ---------------- Product cases dimension ----------------
Kozed60      = Case(16.00, 10.00, 10.00)   
Kozed24      = Case(15.50, 10.00,  4.80)   
Crisup24     = Case(20.39, 12.60,  8.85)   
Crisup20     = Case(15.94, 13.19,  5.12)   
CandyMaster  = Case(15.50,  9.00,  6.20)   

# 函数里查 Case
CASES: Dict[str, Case] = {
    "Kozed60": Kozed60,
    "Kozed24": Kozed24,
    "Crisup24": Crisup24,
    "Crisup20": Crisup20,
    "CandyMaster": CandyMaster,
}

# 要求可以混向拼装
def mixed_orient_layer_capacity(case: Case, L=PALLET_L, W=PALLET_W) -> int:
    """
    同层可混向：未旋转(LxW) + 旋转90°(WxL)；高度不参与旋转。
    思路：把地面切成‘未旋转条带 + 旋转条带’，两种方向各穷举一次，取最大。
    """
    L1, W1 = case.L, case.W      # 未旋转占地
    L2, W2 = case.W, case.L      # 旋转90°占地
    best = 0

    # A) 按宽度切分
    max_rows_unrot = math.floor(W / W1)
    for r in range(max_rows_unrot + 1):
        used_w = r * W1
        if used_w > W: break
        cols_unrot = math.floor(L / L1)
        cnt_unrot  = r * cols_unrot
        rem_w = W - used_w
        rows_rot = math.floor(rem_w / W2)
        cols_rot = math.floor(L / L2)
        cnt_rot  = rows_rot * cols_rot
        best = max(best, cnt_unrot + cnt_rot)

    # B) 按长度切分
    max_cols_unrot = math.floor(L / L1)
    for c in range(max_cols_unrot + 1):
        used_l = c * L1
        if used_l > L: break
        rows_unrot = math.floor(W / W1)
        cnt_unrot  = c * rows_unrot
        rem_l = L - used_l
        cols_rot = math.floor(rem_l / L2)
        rows_rot = math.floor(W / W2)
        cnt_rot  = cols_rot * rows_rot
        best = max(best, cnt_unrot + cnt_rot)

    # 纯单向兜底
    pure1 = math.floor(L / L1) * math.floor(W / W1)
    pure2 = math.floor(L / L2) * math.floor(W / W2)
    return max(best, pure1, pure2)

# ---------------- 每层容量（固定 / 计算） ----------------
PER_LAYER: Dict[str, int] = {
    "Kozed60":     12,  # 固定
    "Kozed24":     12,  # 固定
    "CandyMaster": 12,  # 固定
    "Crisup20":     9,  # 固定
    # Crisup24 默认“混向最优”；如需固定为 6/层或 7/层，改成 6 或 7 即可：
    "Crisup24": mixed_orient_layer_capacity(Crisup24),
}

# ---------------- 层数与每板容量（A 无上限，按高度计算） ----------------
def layers_at_height(case: Case) -> int:
    return math.floor(PALLET_H / case.H)

CPP = {
    "Kozed60":     lambda: PER_LAYER["Kozed60"]     * layers_at_height(Kozed60),
    "Kozed24":     lambda: PER_LAYER["Kozed24"]     * layers_at_height(Kozed24),
    "Crisup24":    lambda: PER_LAYER["Crisup24"]    * layers_at_height(Crisup24),
    "Crisup20":    lambda: PER_LAYER["Crisup20"]    * layers_at_height(Crisup20),
    "CandyMaster": lambda: PER_LAYER["CandyMaster"] * layers_at_height(CandyMaster),
}

# ---------------- 整板优先（也作为默认层序：自下而上） ----------------
FULL_PALLET_ORDER = ["Kozed60", "Kozed24", "CandyMaster", "Crisup24", "Crisup20"]

# ---------------- 先做整板（含逐层明细） ----------------
def carve_full_pallets(orders: Dict[str, int]) -> Tuple[List[Dict], Dict[str,int]]:
    pallets: List[Dict] = []
    remain = orders.copy()
    for sku in FULL_PALLET_ORDER:
        q = remain.get(sku, 0)
        if q <= 0:
            continue
        per = CPP[sku]()
        k = q // per
        if k <= 0:
            continue
        case_layers = layers_at_height(CASES[sku])
        per_layer  = PER_LAYER[sku]
        for _ in range(k):
            layer_plan = []
            for li in range(1, case_layers+1):
                layer_plan.append({"layer": li, "sku": sku, "qty": per_layer})
            pallets.append({"load": {sku: per}, "layer_plan": layer_plan})
        remain[sku] = q - k * per
    return pallets, remain

# ---------------- 枚举“整层”混装 pattern ----------------
def enumerate_patterns() -> List[Dict]:
    max_layers = {sku: layers_at_height(CASES[sku]) for sku in CASES.keys()}
    pats: List[Dict] = []
    for a in range(max_layers["Kozed60"]+1):
        for b in range(max_layers["Kozed24"]+1):
            for e in range(max_layers["CandyMaster"]+1):
                for c in range(max_layers["Crisup24"]+1):
                    for d in range(max_layers["Crisup20"]+1):
                        if a==b==e==c==d==0:
                            continue
                        height = (
                            a*CASES["Kozed60"].H +
                            b*CASES["Kozed24"].H +
                            e*CASES["CandyMaster"].H +
                            c*CASES["Crisup24"].H +
                            d*CASES["Crisup20"].H
                        )
                        if height <= PALLET_H + 1e-6:
                            cap = {
                                "Kozed60":     a*PER_LAYER["Kozed60"],
                                "Kozed24":     b*PER_LAYER["Kozed24"],
                                "CandyMaster": e*PER_LAYER["CandyMaster"],
                                "Crisup24":    c*PER_LAYER["Crisup24"],
                                "Crisup20":    d*PER_LAYER["Crisup20"],
                            }
                            layers = {
                                "Kozed60": a, "Kozed24": b, "CandyMaster": e,
                                "Crisup24": c, "Crisup20": d
                            }
                            pats.append({"layers": layers, "height": height, "cap": cap})
    # 大容量优先，其次高度利用
    pats.sort(key=lambda p: (sum(p["cap"].values()), p["height"]), reverse=True)
    return pats

PATTERNS = enumerate_patterns()

# ---------------- 把某块板的装载量分解成逐层明细 ----------------
def build_layer_plan_from_pattern(load: Dict[str,int], pat_layers: Dict[str,int]) -> List[Dict]:
    plan: List[Dict] = []
    layer_index = 1
    for sku in FULL_PALLET_ORDER:
        qty = load.get(sku, 0)
        if qty <= 0:
            continue
        per_layer = PER_LAYER[sku]
        max_layers_for_sku = pat_layers.get(sku, 0)
        full_layers = min(max_layers_for_sku, qty // per_layer)
        rem = qty - full_layers * per_layer
        # 整层
        for _ in range(full_layers):
            plan.append({"layer": layer_index, "sku": sku, "qty": per_layer})
            layer_index += 1
        # 部分层（如果有余量且还有层配额）
        if rem > 0 and full_layers < max_layers_for_sku:
            plan.append({"layer": layer_index, "sku": sku, "qty": rem})
            layer_index += 1
    return plan

# ---------------- 混装（贪心 + 小合并）：权重体现优先级 ----------------
def pack_mixed(remain: Dict[str,int]) -> Tuple[int, List[Dict]]:
    rem = {k:v for k,v in remain.items() if v>0}
    pallets: List[Dict] = []
    WEIGHTS = {"Kozed60":1.3, "Kozed24":1.2, "CandyMaster":1.2, "Crisup24":1.0, "Crisup20":1.0}

    def score(p):
        cap = p["cap"]
        take_sum = sum(min(rem.get(k,0), v) for k,v in cap.items())
        cap_sum  = sum(cap.values()) or 1
        fill     = take_sum / cap_sum      # 填充率（惩罚半层）
        eff      = sum(min(rem.get(k,0), v) * WEIGHTS.get(k,1.0) for k,v in cap.items())
        return eff * (0.6 + 0.4*fill)

    while any(rem.get(s,0)>0 for s in CASES.keys()):
        best = max(PATTERNS, key=score)
        cap  = best["cap"]
        lays = best["layers"]
        load: Dict[str,int] = {}
        for k, cap_k in cap.items():
            if cap_k>0 and rem.get(k,0)>0:
                take = min(cap_k, rem[k])  # 允许层内不满；评分已惩罚
                if take>0:
                    load[k] = take
                    rem[k] -= take
        if not load:
            # 兜底：剩余最多的 SKU 做单品一板
            k = max(rem.keys(), key=lambda s: rem[s])
            per = CPP[k](); take = min(per, rem[k])
            load = {k: take}; lays = {k: layers_at_height(CASES[k])}
            rem[k] -= take
        layer_plan = build_layer_plan_from_pattern(load, lays)
        pallets.append({"load": load, "layer_plan": layer_plan})

    # 小合并：若有 pattern 可以容纳两块板的合计，则合并
    merged = True
    while merged and len(pallets) >= 2:
        merged = False
        for i in range(len(pallets)-1):
            for j in range(i+1, len(pallets)):
                comb_load = {k: pallets[i]["load"].get(k,0) + pallets[j]["load"].get(k,0) for k in CASES.keys()}
                fit = None
                for p in PATTERNS:
                    if all(comb_load.get(k,0) <= p["cap"].get(k,0) for k in CASES.keys()):
                        fit = p; break
                if fit:
                    comb_plan = build_layer_plan_from_pattern(comb_load, fit["layers"])
                    pallets[i] = {"load": comb_load, "layer_plan": comb_plan}
                    pallets.pop(j)
                    merged = True
                    break
            if merged: break
    return len(pallets), pallets

# ---------------- 入口 ----------------
def plan_min_pallets(orders: Dict[str,int]) -> Tuple[int, List[Dict]]:
    # 单品短路（也生成层计划）
    nz = [k for k,v in orders.items() if v>0]
    if len(nz) <= 1:
        if not nz: return 0,[]
        sku = nz[0]; per = CPP[sku]()
        case_layers = layers_at_height(CASES[sku])
        per_layer   = PER_LAYER[sku]
        pallets: List[Dict] = []
        qty = orders[sku]
        while qty > 0:
            take = min(per, qty)
            full_layers = min(case_layers, take // per_layer)
            rem = take - full_layers*per_layer
            layer_plan = []
            li = 1
            for _ in range(full_layers):
                layer_plan.append({"layer": li, "sku": sku, "qty": per_layer}); li += 1
            if rem > 0 and full_layers < case_layers:
                layer_plan.append({"layer": li, "sku": sku, "qty": rem})
            pallets.append({"load": {sku: take}, "layer_plan": layer_plan})
            qty -= take
        return len(pallets), pallets

    # 先做整板（Kozed60 -> Kozed24 -> CandyMaster -> Crisup24 -> Crisup20）
    full, remain = carve_full_pallets(orders)
    # 再混装
    mix_n, mix_plan = pack_mixed(remain)
    return len(full)+mix_n, full+mix_plan

# ---------------- test ----------------
if __name__ == "__main__":
    print("每层容量（固定/计算）：", PER_LAYER)
    print("每板容量（@60in）：", {k: CPP[k]() for k in PER_LAYER.keys()})

    # test
    orders = {"Kozed60": 0, "Kozed24": 0, "Crisup24": 0, "Crisup20": 250, "CandyMaster": 0}
    total, pallets = plan_min_pallets(orders)
    print(f"\n订单 {orders} -> 需要 {total} 个 pallet")
    for i, pal in enumerate(pallets, 1):
        print(f"\nPallet {i}: load={pal['load']}")
        for row in pal["layer_plan"]:
            print(f"  Layer {row['layer']:>2}: {row['sku']} x {row['qty']}")


# In[ ]:




