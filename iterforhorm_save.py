import pandas as pd
import itertools
import numpy as np
import pyarrow as pa
from collections import Counter
from matplotlib import pyplot as plt
import pyarrow.parquet as pq 
import sys

# Data for permutations
contraceptives = [['ring']]
cost_effectiveness = ['v_unp', 'unp', 'sl_unp', 'neutral', 'sl_imp', 'imp', "v_imp"]
partner_willingness = ['v_unp', 'unp', 'sl_unp', 'neutral', 'sl_imp', 'imp', "v_imp"]
pregnancy_prevention = ['v_unp', 'unp', 'sl_unp', 'neutral', 'sl_imp', 'imp', "v_imp"]
prevents_sti = ['v_unp', 'unp', 'sl_unp', 'neutral', 'sl_imp', 'imp', "v_imp"]
management_of_periods = ['v_unp', 'unp', 'sl_unp', 'neutral', 'sl_imp', 'imp', "v_imp"]
weight_management = ['v_unp', 'unp', 'sl_unp', 'neutral', 'sl_imp', 'imp', "v_imp"]
hormones_used = ['ep', 'p', 'none']
willingness_vagina = ['v_unp', 'unp', 'sl_unp', 'neutral', 'sl_imp', 'imp', "v_imp"]
medical_practitioner = ['v_unp', 'unp', 'sl_unp', 'neutral', 'sl_imp', 'imp', "v_imp"]
medical_procedure = ['v_unp', 'unp', 'sl_unp', 'neutral', 'sl_imp', 'imp', "v_imp"]
acne = ['no', 'mild', 'moderate', 'severe']
acne_2 = ['no', 'yes']
anxiety = ['no', 'mild', 'moderate', 'severe']
depression = ['no', 'mild', 'moderate', 'severe']
hyper = ['no', 'yes']
bclots = ['no', 'yes']
chf_cad = ['no', 'yes']
breast = ['no', 'yes']
smoker = ['no', 'yes']
migraine = ['no', 'yes']
pcos = ['no', 'yes']
endmt = ['no', 'yes']
tgd = ['no', 'mild', 'moderate', 'severe']
ts = ['no', 'yes']
bgdper = ['no', 'mild', 'moderate', 'severe']
bgdper_2 = ['no', 'yes']
gd_vaginal_insertion = ['no', 'mild', 'moderate', 'severe']
gdp = ['no', 'mild', 'moderate', 'severe']
gdp_2 = ['no', 'yes']
hrt = ['no', 'yes']
pref_mana = list(itertools.product(pregnancy_prevention, management_of_periods))
weight_management_hormones = list(itertools.product(weight_management, hormones_used))
medical_practitioner_procedure = list(itertools.product(medical_practitioner, medical_procedure))
acne_anxiety = list(itertools.product(acne, anxiety))
dep_bgdper = list(itertools.product(depression, bgdper))

ceff_preg = list(itertools.product(cost_effectiveness, pregnancy_prevention))
mana_weight = list(itertools.product(management_of_periods, weight_management))
hor_medical = list(itertools.product(hormones_used, medical_practitioner))
depression_breast = list(itertools.product(depression, breast))
pcos_endmt = list(itertools.product(pcos, endmt))
bgdper_gdp = list(itertools.product(bgdper, gdp))
contraceptive_h_iud = [['hormonal_iud']]

willingness_vagina_medic = list(itertools.product(willingness_vagina, medical_practitioner))
procedure_acne = list(itertools.product(medical_procedure, acne))
anx_dep = list(itertools.product(anxiety, depression))
bre_pcos = list(itertools.product(breast, pcos))
endmt_bgdper = list(itertools.product(endmt, bgdper))
gd_vaginal_insertion_gdp = list(itertools.product(gd_vaginal_insertion, gdp))

def scoring_hormonal_iud(perm):
    """
    Scores hormonal IUD based on user preferences and conditions.
    perm: A list containing ["hormonal_iud", pref_mana, weight_management_hormones, 
          willingness_vagina_medic, procedure_acne, anx_dep, bre_pcos, endmt_bgdper, 
          gd_vaginal_insertion_gdp]
    """
    hormonal_iud_score = 3
    
    # Unpack the paired variables
    pref_mana = perm[1]  # (pregnancy_prevention, management_of_periods)
    weight_man_hormones = perm[2]  # (weight_management, hormones_used)
    willingness_med = perm[3]  # (willingness_vagina, medical_practitioner)
    proc_acne = perm[4]  # (medical_procedure, acne)
    anxiety_depression = perm[5]  # (anxiety, depression)
    breast_pcos = perm[6]  # (breast, pcos)
    endmt_bgdper = perm[7]  # (endmt, bgdper)
    gd_insertion_gdp = perm[8]  # (gd_vaginal_insertion, gdp)
    
    # Pregnancy Prevention (from pref_mana[0])
    score_map = {
        "v_unp": -3, "unp": -2, "sl_unp": -1, "neutral": 0,
        "sl_imp": 1, "imp": 2, "v_imp": 3
    }
    hormonal_iud_score += score_map.get(pref_mana[0], 0)
    
    # Management of Periods (from pref_mana[1])
    hormonal_iud_score += score_map.get(pref_mana[1], 0)
    
    # Weight Management (from weight_man_hormones[0])
    hormonal_iud_score -= score_map.get(weight_man_hormones[0], 0)  # Note: reversed scoring
    
    # Hormones Used (from weight_man_hormones[1])
    if weight_man_hormones[1] == 'p':
        hormonal_iud_score += 3
    
    # Willingness Vagina (from willingness_med[0])
    hormonal_iud_score += score_map.get(willingness_med[0], 0)
    
    # Medical Practitioner (from willingness_med[1])
    hormonal_iud_score += score_map.get(willingness_med[1], 0)
    
    # Medical Procedure (from proc_acne[0])
    hormonal_iud_score += score_map.get(proc_acne[0], 0)
    
    # Acne (from proc_acne[1])
    acne_score_map = {
        "no": 0,
        "mild": -15,
        "moderate": -25,
        "severe": -50
    }
    hormonal_iud_score += acne_score_map.get(proc_acne[1], 0)
    
    # Anxiety and Depression (from anxiety_depression)
    for condition in anxiety_depression:
        if condition == 'no':
            continue
        elif condition == 'mild' and anxiety_depression[0 if condition == anxiety_depression[1] else 1] != 'no':
            hormonal_iud_score -= 7.5
        elif condition == 'moderate' and anxiety_depression[0 if condition == anxiety_depression[1] else 1] != 'no':
            hormonal_iud_score -= 12.5
        elif condition == 'severe' and anxiety_depression[0 if condition == anxiety_depression[1] else 1] != 'no':
            hormonal_iud_score -= 25
        elif condition == 'mild' and anxiety_depression[0 if condition == anxiety_depression[1] else 1] == 'no':
            hormonal_iud_score -= 15
        elif condition == 'moderate' and anxiety_depression[0 if condition == anxiety_depression[1] else 1] == 'no':
            hormonal_iud_score -= 25
        elif condition == 'severe' and anxiety_depression[0 if condition == anxiety_depression[1] else 1] == 'no':
            hormonal_iud_score -= 50
    
    # Breast Cancer (from breast_pcos[0])
    if breast_pcos[0] == 'yes':
        hormonal_iud_score -= 100
    
    # PCOS (from breast_pcos[1])
    if breast_pcos[1] == 'yes':
        hormonal_iud_score += 3
    
    # Endometriosis (from endmt_bgdper[0])
    if endmt_bgdper[0] == 'yes':
        hormonal_iud_score += 3
    
    # Background Gender Dysphoria (from endmt_bgdper[1])
    if endmt_bgdper[1] == 'yes':
        hormonal_iud_score += 3
    
    # Gender Dysphoria - Vaginal Insertion (from gd_insertion_gdp[0])
    gd_score_map = {
        "no": 0,
        "mild": -15,
        "moderate": -25,
        "severe": -50
    }
    hormonal_iud_score += gd_score_map.get(gd_insertion_gdp[0], 0)
    
    # Gender Dysphoria General (from gd_insertion_gdp[1])
    if gd_insertion_gdp[1] == 'yes':
        hormonal_iud_score += 3
    
    return hormonal_iud_score

lst = []
row = 0
for i in pref_mana:
    for j in weight_management_hormones:
        for k in willingness_vagina_medic:
            for l in procedure_acne:
                for m in anx_dep:
                    for n in bre_pcos:
                        for o in endmt_bgdper:
                            for p in gd_vaginal_insertion_gdp:
                                perm = ["hormonal_iud", i, j, k, l, m, n, o, p]
                                score = scoring_hormonal_iud(perm)
                                lst.append([row, score])
scores = [item[1] for item in lst]
np.savez_compressed('hormonal_iud_scores.npz', data=lst)


# Calculate minimum, maximum, and median scores
min_score = np.min(scores)
max_score = np.max(scores)
median_score = np.median(scores)

print(f"Minimum score: {min_score}")
print(f"Maximum score: {max_score}")
print(f"Median score: {median_score}")

score_counts = Counter(scores)

# Generate bar graph for each score and its frequency
plt.bar(score_counts.keys(), score_counts.values(), edgecolor='black')
plt.title('Score Frequency Bar Graph')
plt.xlabel('Scores')
plt.ylabel('Frequency')
plt.show()