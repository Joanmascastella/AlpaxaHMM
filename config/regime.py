from dataclasses import dataclass

@dataclass
class RegimeConfig:
    asset_type:             str = ""
    ticker:                 str = ""
    start_date:             str = ""   
    end_date:               str = ""  
    data_cardinality:       str = ""
    data_cardinality_label: str = ""
    feature_set:            str = ""
    regime_interval:        str = ""
    output_path:            str = ""