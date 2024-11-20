# thanks https://github.com/Boris-Filin/NeditGD

NAME_TO_ID = {
    'id': 1,  # +
    'x': 2,  # +
    'y': 3,  # +
    'horizontal_flip': 4,  # +
    'vertical_flip': 5,  # +
    'rotation': 6,  # +
    'trigger_red': 7,
    'trigger_green': 8,
    'trigger_blue': 9,
    'duration': 10,  # +
    'touch_triggered': 11,  # +
    'secret_coin_id': 12,
    'portal_checked': 13,
    'tint_ground': 14,
    'player_color_1': 15,
    'player_color_2': 16,
    'blending': 17,
    '1pt9_color_channel_id': 19,
    'editor_layer_1': 20,
    'color': 21,
    'color_2': 22,
    'target_color': 23,
    'z_layer': 24,
    'z_order': 25,
    'move_x': 28,
    'move_y': 29,
    'easing': 30,
    'text': 31,
    'scale': 32,
    'group_parent': 34,
    'opacity': 35,
    'active_trigger': 36,
    'hsv_enabled': 41,
    'color_2_hsv_enabled': 42,
    'hsv': 43,
    'color_2_hsv': 44,
    'fade_in': 45,
    'hold': 46,
    'fade_out': 47,
    'pulse_hsv': 48,
    'copied_color_hsv': 49,
    'copied_color_id': 50,
    'target': 51,
    'target_type': 52,
    'yellow_teleportation_portal_distance': 54,
    'activate_group': 56,
    'groups': 57,
    'lock_to_player_x': 58,
    'lock_to_player_y': 59,
    'copy_opacity': 60,
    'editor_layer_2': 61,
    'spawn_triggered': 62,
    'spawn_duration': 63,
    'dont_fade': 64,
    'main_only': 65,
    'detail_only': 66,
    'dont_enter': 67,
    'rotate_degrees': 68,
    'times_360': 69,
    'lock_object_rotation': 70,
    'target_pos': 71,  # follow target, move target, sfx target group 2
    'x_mod': 72,
    'y_mod': 73,
    'strength': 75,
    'animation_id': 76,
    'count': 77,
    'subtract_count': 78,
    'pickup_mode': 79,
    'item_id': 80,
    'hold_mode': 81,
    'toggle_mode': 82,
    'interval': 84,
    'easing_rate': 85,
    'exclusive': 86,
    'multi_trigger': 87,
    'comparison': 88,
    'dual_mode': 89,
    'speed': 90,
    'delay': 91,
    'y_offset': 92,
    'activate_on_exit': 93,
    'dynamic_block': 94,
    'block_b': 95,
    'glow_disabled': 96,
    'rotation_speed': 97,
    'disable_rotation': 98,
    'orb_multi_activate': 99,
    'use_target': 100,
    'target_pos_axes': 101,
    'editor_disable': 102,
    'high_detail': 103,
    'count_multi_activate': 104,
    'max_speed': 105,
    'randomize_start': 106,
    'animation_speed': 107,
    'linked_group': 108,
    'camera_zoom': 109,
    'free_mode': 111,
    'edit_free_cam_settings': 112,
    'free_cam_easing': 113,
    'free_cam_padding': 114,
    'ord': 115,
    'no_effects': 116,
    'reversed': 118,
    'song_start': 119,
    'time_mod': 120,
    'no_touch': 121,
    'animate_on_trigger': 123,
    'scale_x': 128,
    'scale_y': 129,
    'perspective_x': 131,
    'perspective_y': 132,
    'only_move': 133,
    'passable': 134,
    'hide': 135,
    'nonstick_x': 136,
    'ice_block': 137,
    'player_1': 138,
    'override_count': 139,
    'follow_camera_x': 141,
    'follow_camera_y': 142,
    'follow_camera_x_mod': 143,
    'follow_camera_y_mod': 144,  # caution, if = 0.0, restores to default 1.0 after reloading
    'particle_setup': 145,
    'use_obj_color': 146,
    'gravity': 148,
    'scale_x_by': 150,
    'scale_y_by': 151,
    'group_probabilities': 152,
    'div_by_x': 153,
    'div_by_y': 154,
    'streak_additive': 159,
    'unlink_dual_gravity': 160,
    'hide_ground': 161,
    'hide_p1': 162,
    'hide_p2': 163,
    'camera_edge': 164,
    'keep_velocity': 169,
    'change_channel': 171,
    'grip_slope': 193,
    'hide_mg': 195,
    'player_only': 198,
    'disable_controls_p1': 199,
    'player_2': 200,
    '_pt': 201,
    'gradient_layer': 202,
    'gradient_bl': 203,
    'gradient_br': 204,
    'gradient_tl': 205,
    'gradient_tr': 206,
    'gradient_vertex_mode': 207,
    'gradient_disable': 208,
    'gradient_id': 209,
    'quick_start': 211,
    'follow_group': 212,
    'follow_easing': 213,
    'follow_p1': 215,
    'follow_p2': 216,
    'aream_move_dist': 218,
    'area_offset': 220,
    'area_length': 222,
    'effect_id': 225,
    'area_move_angle': 231,
    'area_scale_x': 233,
    'area_scale_y': 235,
    'area_move_x': 237,
    'area_move_y': 239,
    'area_xy_mode': 241,
    'area_easing': 242,
    'area_direction': 262,
    'mod_front': 263,
    'mod_back': 264,
    'parent_groups': 274,
    'area_inwards': 276,
    'area_parent': 279,
    'deadzone': 282,
    'area_mirrored': 283,
    'nonstick_y': 289,
    'effect_priority': 341,
    'enter_channel': 343,
    'scale_stick': 356,
    'disable_grid_snap': 370,
    'no_audio_scale': 372,
    'follow_mode': 394,
    'center_group_id': 395,
    'target_move_distance': 396,
    'rotation_dynamic': 397,
    'rotation_target': 401,
    'rotation_offset': 402,
    'events': 430,
    'sequence': 435,
    'seq_mode': 436,
    'seq_min_int': 437,
    'seq_reset': 438,
    'seq_reset_type': 439,
    'spawn ordered': 441,
    'spawn_remap': 442,
    'material': 446,
    'pickup_mod': 449,
    'preview_opacity': 456,
    'timer_display': 466,
    'timer_start': 467,
    'no_timer_override': 468,
    'ignore_time_warp': 469,
    'timer_mod': 470,
    'timer_paused': 471,
    'timer_control': 472,
    'timer_target': 473,
    'timer_stop': 474,
    'timer_multi_active': 475,
    'item_type_1': 476,
    'item_type_2': 477,
    'item_type_3': 478,
    'num_mod': 479,
    'num_op_1': 480,
    'num_op_2': 481,
    'num_op_3': 482,
    'num_mod_2': 483,
    'num_offset': 484,
    'round_op_1': 485,
    'round_op_2': 486,
    'set_persistent': 491,
    'pers_target_all': 492,
    'pers_reset': 493,
    'pers_timer': 494,
    'extra_sticky': 495,
    'dont_boost_y': 496,
    'seq_unique_remap': 505,
    'no_particle': 507,
    'dont_boost_x': 509,
    'extended_collision': 511,
    'event_target': 525,
    'dont_edit_area_parent': 539,
    'neg_op_1': 578,
    'neg_op_2': 579,
}

additional = {
    'sfx_unique_id': 416,
    'sfx_group': 455,
    # Used in PlayLayer::updateVisibility during LevelEditorLayer::onPlaytest as index of some Level
    # When you 'Edit object' hsv the game tries to find similar cached hsv and stores its index in object.
    # This is probably for memory optimization reasons. Base and Detail indexes aren't combinable.
    'hsv_base_index': 155,
    'hsv_detail_index': 156,

    'pulse_nonstatic_hsv': 210,

    'spawn_duration_variation': 556,  # delay += variation * random.uniform(-1, 1)
    'reset_remap': 581,

    'stop_mode': 580,  # 0 - stop, 1 - pause, 2 - resume
    'use_control_id': 535,  # stop trigger

    'text_align': 391,  # display
    'seconds_only': 389,
    'display_special': 390,  # -1: MainTime, -2: Points, -3: Attempts

    'player_player_collision': 201,  # PP in collision

    # ToggleBlock
    'claim_touch': 445,
    'no_multi_activate': 444,
    'spawn_only': 504,

    # in aim mode: rot target's position is clamped to this borders
    'rotation_min_x': 516,
    'rotation_max_x': 517,
    'rotation_min_y': 518,
    'rotation_max_y': 519,

    'rotation_dynamic_easing': 403,  # in aim mode rotation speed is proportional to delta angle divided by easing. For easing=100 it takes ~2.9s to rotate from 180 to 90 degrees

    'text_kerning': 488,
    'move_small_steps': 393,
}

del NAME_TO_ID['_pt']
if NAME_TO_ID.keys() & additional:
    print(NAME_TO_ID.keys() & additional)

NAME_TO_ID.update(additional)


def print_missing():
    prev = 0
    missing = []
    for v in sorted(NAME_TO_ID.values()):
        if v - prev == 2:
            print(v - 1)
        elif v - prev == 3:
            print(prev + 1)
            print(v - 1)
        elif v - prev > 3:
            print(f'{prev + 1} ... {v - 1}')
        prev = v
    print(missing)


if __name__ == '__main__':
    print_missing()
