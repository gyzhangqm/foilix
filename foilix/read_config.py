# coding: utf-8

r"""Case config read"""

from configobj import ConfigObj


def read_config(path):
    r"""Read the config file
    
    Parameters
    ----------
    path : str
        Path to the config file

    Returns
    -------
    dict

    """

    config = {}

    c = ConfigObj(path)

    config["foil_dat_folder"] = c["paths"]["foil_dat_folder"]
    config["foil_data_folder"] = c["paths"]["foil_data_folder"]

    config["aoa_spec"] = [float(e) for e in c["context"]["aoa_spec"]]
    config["reynolds_numbers"] = [float(e) for e in c["context"]["reynolds_numbers"]]
    config["ncrits"] = [float(e) for e in c["context"]["ncrits"]]

    config["aoa_ld"] = [float(e) for e in c["scoring"]["aoa_ld"]]
    config["inv_min_drag_scaling"] = float(c["scoring"]["inv_min_drag_scaling"])

    config["ta_plus_minus"] = float(c["nurbs"]["ta_plus_minus"])
    config["tb_plus_minus"] = float(c["nurbs"]["tb_plus_minus"])
    config["alpha_plus_minus"] = float(c["nurbs"]["alpha_plus_minus"])

    config["thickness_plus_minus"] = float(c["parsec"]["thickness_plus_minus"])
    config["max_thickness_x_plus_minus"] = float(c["parsec"]["max_thickness_x_plus_minus"])
    config["curvature_plus_minus"] = float(c["parsec"]["curvature_plus_minus"])
    config["le_radius_plus_minus"] = float(c["parsec"]["le_radius_plus_minus"])
    config["te_angle_plus_minus"] = float(c["parsec"]["te_angle_plus_minus"])

    return config

if __name__ == "__main__":
    print(read_config("foilix_case.conf"))
