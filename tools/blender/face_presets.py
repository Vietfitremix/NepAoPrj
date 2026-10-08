"""Bộ khuôn mặt (trọng số target MakeHuman, CC0) cho người mẫu nữ/nam. Dùng chung cho face_preview.py và render_model.py.

Tên target = đường dẫn tương đối trong data/targets (không có .target.gz). Target có tiền tố "l-/r-" được áp cả hai bên.
"""
EYEBROWS = {"nu": "eyebrow006", "nam": "eyebrow002"}
EYELASHES = {"nu": "eyelashes02", "nam": "eyelashes01"}
HAIR = {"nu": "elvs_reverse_french_braid_bun", "nam": "culturalibre_hair_05"}
FACE = {"nu": "thanh_tu", "nam": "thu_sinh"}                 # bộ mặt đã chốt
SMILE = "expression/units/asian/mouth-corner-puller"

PRESETS = {
    "nu": {
        "thanh_tu": {"head/head-oval": 0.6, "chin/chin-width-decr": 0.3, "eyes/*-eye-scale-incr": 0.25,
                     "eyes/*-eye-height2-incr": 0.3, "nose/nose-scale-horiz-decr": 0.25, "nose/nose-point-width-decr": 0.3,
                     "mouth/mouth-upperlip-volume-incr": 0.2, "mouth/mouth-lowerlip-volume-incr": 0.3,
                     "mouth/mouth-angles-up": 0.4, SMILE: 0.25, "cheek/*-cheek-volume-incr": 0.2},
        "tron_hien": {"head/head-round": 0.4, "cheek/*-cheek-volume-incr": 0.4, "eyes/*-eye-scale-incr": 0.35,
                      "eyes/*-eye-height2-incr": 0.2, "chin/chin-width-decr": 0.2, "nose/nose-scale-horiz-decr": 0.15,
                      "mouth/mouth-angles-up": 0.5, SMILE: 0.35},
        "trai_xoan": {"head/head-invertedtriangular": 0.4, "cheek/*-cheek-bones-incr": 0.3, "chin/chin-prominent-incr": 0.2,
                      "eyes/*-eye-corner2-up": 0.3, "eyes/*-eye-scale-incr": 0.2, "nose/nose-point-width-decr": 0.3,
                      "nose/nose-scale-vert-incr": 0.1, "mouth/mouth-lowerlip-volume-incr": 0.2,
                      "mouth/mouth-angles-up": 0.35, SMILE: 0.2},
    },
    "nam": {
        "thu_sinh": {"head/head-oval": 0.4, "chin/chin-width-decr": 0.15, "eyes/*-eye-scale-incr": 0.15,
                     "nose/nose-point-width-decr": 0.2, "mouth/mouth-angles-up": 0.3, SMILE: 0.2,
                     "eyebrows/eyebrows-trans-down": 0.1},
        "vuong_khoe": {"head/head-square": 0.4, "chin/chin-width-incr": 0.2, "chin/chin-prominent-incr": 0.25,
                       "cheek/*-cheek-bones-incr": 0.3, "eyes/*-eye-scale-incr": 0.1, "mouth/mouth-angles-up": 0.3,
                       SMILE: 0.25},
        "hien_tuoi": {"head/head-round": 0.3, "cheek/*-cheek-volume-incr": 0.2, "eyes/*-eye-scale-incr": 0.25,
                      "eyes/*-eye-height2-incr": 0.15, "mouth/mouth-angles-up": 0.45, SMILE: 0.35,
                      "nose/nose-scale-horiz-decr": 0.1},
    },
}


def apply_face(human, targets_dir, preset: dict):
    """Nạp target khuôn mặt lên basemesh (gọi TRƯỚC khi gắn tóc/lông mày để chúng khớp mặt mới)."""
    from bl_ext.user_default.mpfb.services.targetservice import TargetService
    for name, w in preset.items():
        for n in ([name.replace("*", s) for s in ("l", "r")] if "*" in name else [name]):
            TargetService.load_target(human, str(targets_dir / f"{n}.target.gz"), weight=w, name=n.split("/")[-1])
