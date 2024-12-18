from bidict import bidict

# special_ids = {
#     31: 'StartPos',
#     899: 'Color',
#     901: 'Move',
#     1616: 'Stop',
#     1006: 'Pulse',
#     1007: 'Alpha',
#     1049: 'Toggle',
#     1268: 'Spawn',
#     1346: 'Rotate',
#     2067: 'Scale',
#     1347: 'Follow',
#     1520: 'Shake',
#     1585: 'Animate',
#     3033: 'Keyframe',
#     1814: 'FollowPlayerY',
#     3016: 'AdvancedFollow',
#     3660: 'EditAdvFollow',
#     3661: 'ReTargetAdvFollow',
#     3032: 'KeyframeNode',
#     3006: 'AreaMove',
#     3007: 'AreaRotate',
#     3008: 'AreaScale',
#     3009: 'AreaFade',
#     3010: 'AreaTint',
#     3011: 'EditAreaMove',
#     3012: 'EditAreaRotate',
#     3013: 'EditAreaScale',
#     3014: 'EditAreaFade',
#     3015: 'EditAreaTint',
#     3024: 'AreaStop',
#     3029: 'ChangeBackground',
#     3030: 'ChangeGround',
#     3031: 'ChangeMiddleground',
#     1595: 'Touch',
#     1611: 'Count',
#     1811: 'InstantCount',
#     1817: 'Pickup',
#     3614: 'Time',
#     3615: 'TimeEvent',
#     3617: 'TimeControl',
#     3619: 'ItemEdit',
#     3620: 'ItemCompare',
#     3641: 'ItemPersistent',
#     1912: 'Random',
#     2068: 'AdvancedRandom',
#     3607: 'Sequence',
#     3608: 'SpawnParticles',
#     3618: 'ResetPickups',
#     1913: 'CameraZoom',
#     1914: 'CameraStatic',
#     1916: 'CameraOffset',
#     2901: 'CameraGameplayOffset',
#     2015: 'CameraRotation',
#     2062: 'CameraEdge',
#     2925: 'CameraMode',
#     2016: 'CameraGuide',
#     1917: 'Reverse',
#     2900: 'RotateGameplay',
#     1934: 'Song',
#     3605: 'EditSong',
#     3602: 'Sfx',
#     3603: 'EditSfx',
#     3604: 'PLayerEvent',
#     1935: 'TimeWarp',
#     2999: 'SetupMiddleground',
#     3606: 'BackgroundSpeed',
#     3612: 'MiddlegroundSpeed',
#     1615: 'CounterLabel',
#     3613: 'UIObjectSettings',
#     3662: 'VisibilityLink',
#     1815: 'Collision',
#     3609: 'InstantCollision',
#     3640: 'CollisionState',
#     1816: 'CollisionBlock',
#     3643: 'ToggleBlock',
#     1812: 'OnDeath',
#     33: 'DisableTrace',
#     32: 'EnableTrace',
#     1613: 'ShowPlayer',
#     1612: 'HidePlayer',
#     1818: 'BackgroundEffectOn',
#     1819: 'BackgroundEffectOff',
#     3600: 'End',
#     1932: 'PlayerControl',
#     2899: 'Options',
#     3642: 'GuideBPM',
#     2903: 'Gradient',
#     2066: 'Gravity',
#     3022: 'Teleport',
#     2904: 'Shader',
#     2905: 'ShaderShockWave',
#     2907: 'ShaderShockLine',
#     2909: 'ShaderGlitch',
#     2910: 'ShaderChromatic',
#     2911: 'ShaderChromaGlitch',
#     2912: 'ShaderPixelate',
#     2913: 'ShaderLensCircle',
#     2914: 'ShaderRadialBlur',
#     2915: 'ShaderMotionBlur',
#     2916: 'ShaderBulge',
#     2917: 'ShaderPinch',
#     2919: 'ShaderGrayscale',
#     2920: 'ShaderSepia',
#     2921: 'ShaderInvertColor',
#     2922: 'ShaderHUE',
#     2923: 'ShaderEditColor',
#     2924: 'ShaderSplitScreen',
#     22: 'EnterEffectFade',
#     24: 'EnterEffectUp',
#     23: 'EnterEffectDown',
#     25: 'EnterEffectLeft',
#     26: 'EnterEffectRight',
#     27: 'EnterEffectSmall',
#     28: 'EnterEffectBig',
#     55: 'EnterEffectChaos',
#     56: 'EnterEffectLeftUp',
#     57: 'EnterEffectRightUp',
#     58: 'EnterEffectSplitUp',
#     59: 'EnterEffectSplitDown',
#     1915: 'EnterEffectOff',
#     3017: 'EnterMove',
#     3018: 'EnterRotate',
#     3019: 'EnterScale',
#     3020: 'EnterFade',
#     3021: 'EnterTint',
#     3023: 'EnterStop'
# }

special_ids = bidict({
    # ----- objects behaviour
    901: 'Move',  # +
    1346: 'Rotate',
    2067: 'Scale',
    1007: 'Alpha',
    1585: 'Animate',
    3033: 'Keyframe',
    3032: 'KeyframeNode',
    3613: 'UIObjectSettings',
    3662: 'VisibilityLink',

    1347: 'Follow',
    3016: 'AdvancedFollow',
    3660: 'EditAdvFollow',
    3661: 'ReTargetAdvFollow',
    1814: 'FollowPlayerY',

    3006: 'AreaMove',
    3007: 'AreaRotate',
    3008: 'AreaScale',
    3009: 'AreaFade',
    3010: 'AreaTint',
    3011: 'EditAreaMove',
    3012: 'EditAreaRotate',
    3013: 'EditAreaScale',
    3014: 'EditAreaFade',
    3015: 'EditAreaTint',
    3024: 'AreaStop',

    899: 'Color',
    1006: 'Pulse',

    # ----- control triggers
    1049: 'Toggle',  # +
    1268: 'Spawn',  # +
    1616: 'Stop',  # +
    3607: 'Sequence',
    1912: 'Random',
    2068: 'AdvancedRandom',
    # ----- - item
    1817: 'Pickup',  # +
    1611: 'Count',  # +
    1811: 'InstantCount',  # +
    3619: 'ItemEdit',  # +
    3620: 'ItemCompare',  # +
    3641: 'ItemPersistent',  # +
    1615: 'CounterLabel',  # +
    # ----- - timer
    3614: 'Timer',
    3615: 'TimerEvent',
    3617: 'TimerControl',
    # ----- - player input
    1595: 'Touch',  # +
    3604: 'PLayerEvent',
    1812: 'OnDeath',
    # ----- - collision
    1815: 'Collision',  # +
    3609: 'InstantCollision',  # +
    3640: 'CollisionState',  # +
    1816: 'CollisionBlock',  # +
    3643: 'ToggleBlock',  # +

    # ----- player behaviour
    31: 'StartPos',
    1935: 'TimeWarp',
    1917: 'Reverse',
    2900: 'RotateGameplay',
    3600: 'End',
    1932: 'PlayerControl',
    2899: 'Options',
    2066: 'Gravity',
    3022: 'Teleport',
    # ----- camera
    1913: 'CameraZoom',
    1914: 'CameraStatic',
    1916: 'CameraOffset',
    2901: 'CameraGameplayOffset',
    2015: 'CameraRotation',
    2062: 'CameraEdge',
    2925: 'CameraMode',
    2016: 'CameraGuide',
    1520: 'Shake',
    # ----- sound
    1934: 'Song',
    3605: 'EditSong',
    3602: 'Sfx',
    3603: 'EditSfx',
    # ----- visuals
    33: 'DisableTrace',
    32: 'EnableTrace',
    1613: 'ShowPlayer',
    1612: 'HidePlayer',
    1818: 'BackgroundEffectOn',
    1819: 'BackgroundEffectOff',
    # ----- background
    3029: 'ChangeBackground',
    3030: 'ChangeGround',
    3031: 'ChangeMiddleground',
    2999: 'SetupMiddleground',
    3606: 'BackgroundSpeed',
    3612: 'MiddlegroundSpeed',
    # ----- shader
    2904: 'Shader',
    2905: 'ShaderShockWave',
    2907: 'ShaderShockLine',
    2909: 'ShaderGlitch',
    2910: 'ShaderChromatic',
    2911: 'ShaderChromaGlitch',
    2912: 'ShaderPixelate',
    2913: 'ShaderLensCircle',
    2914: 'ShaderRadialBlur',
    2915: 'ShaderMotionBlur',
    2916: 'ShaderBulge',
    2917: 'ShaderPinch',
    2919: 'ShaderGrayscale',
    2920: 'ShaderSepia',
    2921: 'ShaderInvertColor',
    2922: 'ShaderHUE',
    2923: 'ShaderEditColor',
    2924: 'ShaderSplitScreen',
    # ----- enter effects
    22: 'EnterEffectFade',
    24: 'EnterEffectUp',
    23: 'EnterEffectDown',
    25: 'EnterEffectLeft',
    26: 'EnterEffectRight',
    27: 'EnterEffectSmall',
    28: 'EnterEffectBig',
    55: 'EnterEffectChaos',
    56: 'EnterEffectLeftUp',
    57: 'EnterEffectRightUp',
    58: 'EnterEffectSplitUp',
    59: 'EnterEffectSplitDown',
    1915: 'EnterEffectOff',
    3017: 'EnterMove',
    3018: 'EnterRotate',
    3019: 'EnterScale',
    3020: 'EnterFade',
    3021: 'EnterTint',
    3023: 'EnterStop',

    # ----- special
    3642: 'GuideBPM',
    2903: 'Gradient',
    3608: 'SpawnParticles',
    3618: 'Reset',  # +
    914:  'Text',
    1931: 'End2',  # todo why there's a second end?
})

legacy_ids = bidict({
    34: 'LegacyStartPos',

    221: 'LegacyColor1',  # converts into id 899
    717: 'LegacyColor2',  # converts into id 899
    718: 'LegacyColor3',  # converts into id 899
    743: 'LegacyColor4',  # converts into id 899

    29: 'LegacyColorBG',
    30: 'LegacyColorG1',
    900: 'LegacyColorG2',
    104: 'LegacyColorLineBlending',  # converts into id 915
    915: 'LegacyColorLine',
    105: 'LegacyColorObj',
    744: 'LegacyColor3DL',
})

special_ids.update(legacy_ids)
