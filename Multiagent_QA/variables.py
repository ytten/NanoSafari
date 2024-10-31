txt2json_output_template = '''
{
    "0": {
    "question": "..."
    "conditions": [
            {
                "attribute": ,
                "data_type": ,
                "value":
            },
            ...
        ]   
    "target_attributes": [
            {
                "attribute": ,
                "data_type": ,
                "desired_value":
            },
            ...
        ]
    }
    "1": {
    "question": "..."
    "conditions": [
            {
                "attribute": ,
                "data_type": ,
                "value":
            },
            ...
        ]   
    "target_attributes": [
            {
                "attribute": ,
                "data_type": ,
                "desired_value":
            },
            ...
        ]
    }
}
'''
smaller_schema = [('paper_id', 'int', 'NO', 'PRI', None, 'auto_increment'), 
    ('particle_charge_zeta_potential_mean_mV', 'float', 'YES', '', None, ''), 
    ('particle_charge_zeta_potential_std_mV', 'float', 'YES', '', None, ''), 
    ('animal_age', 'float', 'YES', '', None, ''), 
    ('animal_sex', "enum('male','female','male and female','unknown')", 'YES', '', None, ''),
    ('injected_in_vivo_drug_concentration', 'float', 'YES', '', None, ''), 
    ('gene_length', 'float', 'YES', '', None, ''), 
    ('half_life', 'float', 'YES', '', None, ''), 
    ('loading_efficiency', 'float', 'YES', '', None, ''), 
    ('injected_in_vivo_drug_concentration_unit', "enum('mg/kg','mg/ml','nmol','ng')", 'YES', '', None, ''), 
    ('gene_length_unit', "enum('nt','kb','bp','mer')", 'YES', '', None, ''), 
    ('doi', 'text', 'YES', '', None, ''), 
    ('publication_year', 'int', 'YES', '', None, ''), 
    ('summary', 'text', 'YES', '', None, ''), 
    ('avg_times_cited', 'float', 'YES', '', None, '')]

table_schema = [['paper_id', 'int', 'NO', 'PRI', None, 'auto_increment'],
    ['nanoparticle_type', 'text', 'YES', '', None, ''],
    ['disease', 'text', 'YES', '', None, ''],
    ['payloads', 'text', 'YES', '', None, ''],
    ['surface_modification', 'text', 'YES', '', None, ''],
    ['lipid_cholesterol_ratio', 'text', 'YES', '', None, ''],
    ['particle_size_mean_nm', 'float', 'YES', '', None, ''],
    ['particle_charge_zeta_potential_mean_mV', 'float', 'YES', '', None, ''],
    ['peg_type', 'text', 'YES', '', None, ''],
    ['animal_model', 'text', 'YES', '', None, ''],
    ['animal_species', 'text', 'YES', '', None, ''],
    ['animal_age', 'float', 'YES', '', None, ''],
    ['animal_sex', "enum('male','female','male and female','unknown')", 'YES', '', None, ''],
    ['nanoparticle_drug_administration_routes', 'text', 'YES', '', None, ''],
    ['injected_in_vivo_drug_concentration', 'float', 'YES', '', None, ''],
    ['gene_length', 'float', 'YES', '', None, ''],
    ['intended_targeted_site_of_the_nanoparticle_drug', 'text', 'YES', '', None, ''],
    ['half_life', 'float', 'YES', '', None, ''],
    ['toxicity', 'text', 'YES', '', None, ''],
    ['loading_efficiency', 'float', 'YES', '', None, ''],
    ['biodegradability', 'tinyint(1)', 'YES', '', None, ''],
    ['injected_in_vivo_drug_concentration_unit', "enum('mg/kg','mg/ml','nmol','ng')", 'YES', '', None, ''],
    ['gene_length_unit', "enum('nt','kb','bp','mer')", 'YES', '', None, ''],
    ['article_title', 'text', 'YES', '', None, ''],
    ['doi', 'text', 'YES', '', None, ''],
    ['publication_year', 'int', 'YES', '', None, ''],
    ['summary', 'text', 'YES', '', None, ''],
    ['avg_times_cited', 'float', 'YES', '', None, '']]

vector_elements_list = ['intended_targeted_site_of_the_nanoparticle_drug',
    'surface_modification',
    'animal_species',
    'animal_model',
    'payloads',
    'nanoparticle_drug_administration_routes',
    'nanoparticle_type',
    'disease',
    'summary',
    'peg_type']

text_attr_list = [
            'lipid_ratio',
            'article_title',
            'toxicity',
            'lipid_cholesterol_ratio',
            'doi']

float_attr_list = [
            'particle_size_mean_nm',
            'particle_charge_zeta_potential_mean_mV',
            'animal_age',
            'injected_in_vivo_drug_concentration',
            'gene_length',
            'half_life',
            'loading_efficiency']

sample_questions = '''
        Challenging Case: My intended payload A is a 2000 nt length mRNA. My intended payload B is doxorubicin. Both need to be delivered to brain. What kind of nanoparticles shall be used to deliver A and B, respectively?

        Literature Review: Please provide some examples of using nanoparticles for neuro diseases.
        
        Research Trend: For lipid nanoparticles, what are the new formulations or surface modification commonly used in the past 5 years? How about 10 years ago?

        Experimental Design: How to design a nanoparticle that releases the drug in low pH environment?

        Comparative Issues: The nanoparticle A is 100 nm and its zeta potential is -20 mV. Nanoparticle B is 600 nm and its zeta potential is +15 mV. Both are polystyrene. Which one do you think will have better tumor delivery efficiency? Why?
        '''

sample_question = '''How to design a nanoparticle that releases the drug in low pH environment?'''