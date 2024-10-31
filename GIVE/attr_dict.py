my_attr_dict = {
    "nanoparticle characteristics": [
        "nanoparticle_formulation",
        "nanoparticle_type",
        "lipid_cholesterol_ratio",
        "particle_size_mean_nm",
        "particle_size_std_nm",
        "particle_charge_zeta_potential_mean_mV",
        "particle_charge_zeta_potential_std_mV",
    ],
    "nanaoparticle surface modification":[
        "surface_modification",
        "surface_modification_elaboration",
        "peg_type",
    ],
    "target and purpose":[
        "disease",
        "intended_targeted_site_of_the_nanoparticle_drug",
    ],
    "payload detail":[
        "payloads",
        "drug_molecular_weight",
        "toxicity",
        "gene_length"  
    ],
    "dosage and stability":[
        "injected_in_vivo_drug_concentration",
        "loading_efficiency",
        "half_life",
        "dose_frequencies",
        "drug_blood_concentration",
    ],
    "test animals": [
        "animal_model",
        "animal_species",
        "animal_age",
        "animal_sex",
        "nanoparticle_drug_administration_routes",
        "pk_pd_pharmacokinetics_pharmacodynamics"
    ],
    "clinical trials and safety": [
        "clinical_trial_with_human_subject",
        "clinical_trial_side_effect"
    ],
    "Storage": [
        "drug_stability_in_vivo_stability",
        "storage_condition",
        "biodegradability"
    ]
}
my_attr_dict_small = {
    "nanaoparticle surface modification":[
        "surface_modification_elaboration",
        "peg_type",
    ]
}
my_prompt_dict = {
    "nanoparticle_formulation": "What is the nanoparticle formulation the text mainly introduce? Include the any prefix/suffix appeared. Answer with the formulation only.",
    "nanoparticle_type": "What is the nanoparticle the text mainly introduce? Answer with the nanoparticle type only.",
    "disease": "What specific disease does the text concentrate on? Answer the specific disease only.",
    "payloads": "What are the payloads of the nanoparticle which the text mainly introduce? Answer with the full names of the payloads only.",
    "surface_modification": "What is the surface modification/decoration of the nanoparticle which the text mainly introduce? Answer the surface modification only.",
    "surface_modification_elaboration": "How is the surface modification/decoration of the nanoparticle made? Answer with the elaboration only.",
    "lipid_ratio": "What is the lipid ratio of the nanoparticle mainly introduced in the text? Answer with the lipid ratio weight only.",
    "cholesterol_ratio": "What is the cholesterol ratios of the nanoparticle that the text mainly introduce? Answer with the cholesterol ratio only.",
    "lipid_cholesterol_ratio": "What is the lipid cholesterol ratio of the nanoparticle that the text mainly introduce? Answer with the lipid cholesterol ratio only.",
    "particle_size_mean_nm": "What is the mean particle size of the nanoparticle that the text mainly introduce? The unit of the particle size is 'nm'. Answer with the mean value only.",
    "particle_size_std_nm": "What is the standard deviation of the nanoparticle size that the text mainly introduce? The unit of the particle size is 'nm'. Answer with the standard deviation value only.",
    "particle_charge_zeta_potential_mean_mV": "What is the mean particle charge of the nanoparticle that the text mainly introduce? The unit of the Particle charge is 'mV'. Answer with the mean value only.",
    "particle_charge_zeta_potential_std_mV": "What is the standard deviation of the particle charge of the nanoparticle that the text mainly introduce? The unit of the Particle charge is 'mV'. Answer with the standard deviation value only.",
    "peg_type": "What is the PEG type according to the text? Answer with the PEG type only.",
    "animal_model": "What are the animal models (An animal with a disease either the same as or like a disease in humans) mentioned in this text? Answer the animal models and its disease.",
    "animal_species": "What is the species of the animals that the researchers use to do experiments in this text? Answer the species only.",
    "animal_age": "What is the age of the animals that the researchers use to do experiments in this text? Answer with the age of the animals only.",
    "animal_sex": "What is the sex of the animals that the researchers use to do experiments in this text? Answer with the sex of the animals only.",
    "nanoparticle_drug_administration_routes": "What are the administration routes/injection sites of the nanoparticle/drug/mRNA/siRNA for all mentioned animal models? Answer with the route or sites only.",
    "drug_molecular_weight": "What is the molecular weight of the drug which the researchers mainly use? Answer with the drug molecular weight only.",
    "injected_in_vivo_drug_concentration": "What is the in vivo drug/mRNA/siRNA concentration injected/treated to the animal model according to the given text? Answer with the concentration only.",
    "gene_length": "What is the length of gene/mRNA in the experiment(s)? Answer with the length of gene/mRNA only.",
    "intended_targeted_site_of_the_nanoparticle_drug": "What is the intended targeted site of the nanoparticle/drug according to the text? Answer all mentioned intended targeted sites/organs.",
    "half_life": "What is the half-life of the nanoparticle according to the text? Answer with the half-life time only.",
    "dose_frequencies": "What are the Dose frequency of the nanoparticle according to the text? Answer with the dose frequencies only.",
    "drug_blood_concentration": "What is the drug blood concentration/area under the curve/AUC according to the text? Answer with the drug blood concentration/area under the curve/AUC only.",
    "pk_pd_pharmacokinetics_pharmacodynamics": "What is the PK/PD/Pharmacokinetics/pharmacodynamics according to the text? Answer with the PK/PD only.",
    "loading_efficiency": "What is the loading efficiency of the nanoparticle according to the text? Answer with the loading efficiency only.",
    "clinical_trial_with_human_subject": "What is the clinical trial/investigation detail with human subject according to the text? Answer with the trial/investigation detail only.",
    "clinical_trial_side_effect": "What is the side effect during the clinical trial that involves human subject? Answer with the side effect only.",
    "storage_condition": "What is the storage condition of the nanoparticle according to the text? Answer with the storage condition only.",
    "biodegradability": "What is the biodegradability of the nanoparticle according to the text? Answer with True or False only.",
    "toxicity": "What is the toxicity of the loaded drug according to the text? Answer with the Low or High only.",
    "drug_stability_in_vivo_stability": "Is the drug stable according to the text? Answer with True or False only.",
}
