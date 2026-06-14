// 由 tools/build_assets.py 自動產生。include 後用 MARINE_IMAGES 巨集。
#pragma once
#include "idle.h"
#include "yawn.h"
#include "cheer.h"
#include "pet.h"
#include "eat.h"
#include "sleep.h"
#include "egg.h"
#include "bg_room.h"
#include "end_good.h"
#include "end_normal.h"
#include "end_bad.h"
#include "end_runaway.h"
#include "emo_success.h"
#include "emo_fail.h"
#include "food_0.h"
#include "food_1.h"
#include "food_2.h"
#include "food_3.h"
#include "food_4.h"

// 展開成 ImageAsset 陣列項（含多幀指標），供 character.h 的 IMAGES[] 使用。
#define MARINE_IMAGES \
    {"idle", img_idle_frames, IMG_IDLE_N, IMG_IDLE_W, IMG_IDLE_H, 0xF81F}, \
    {"yawn", img_yawn_frames, IMG_YAWN_N, IMG_YAWN_W, IMG_YAWN_H, 0xF81F}, \
    {"cheer", img_cheer_frames, IMG_CHEER_N, IMG_CHEER_W, IMG_CHEER_H, 0xF81F}, \
    {"pet", img_pet_frames, IMG_PET_N, IMG_PET_W, IMG_PET_H, 0xF81F}, \
    {"eat", img_eat_frames, IMG_EAT_N, IMG_EAT_W, IMG_EAT_H, 0xF81F}, \
    {"sleep", img_sleep_frames, IMG_SLEEP_N, IMG_SLEEP_W, IMG_SLEEP_H, 0xF81F}, \
    {"egg", img_egg_frames, IMG_EGG_N, IMG_EGG_W, IMG_EGG_H, 0xF81F}, \
    {"bg_room", img_bg_room_frames, IMG_BG_ROOM_N, IMG_BG_ROOM_W, IMG_BG_ROOM_H, 0xFFFF}, \
    {"end_good", img_end_good_frames, IMG_END_GOOD_N, IMG_END_GOOD_W, IMG_END_GOOD_H, 0xF81F}, \
    {"end_normal", img_end_normal_frames, IMG_END_NORMAL_N, IMG_END_NORMAL_W, IMG_END_NORMAL_H, 0xF81F}, \
    {"end_bad", img_end_bad_frames, IMG_END_BAD_N, IMG_END_BAD_W, IMG_END_BAD_H, 0xF81F}, \
    {"end_runaway", img_end_runaway_frames, IMG_END_RUNAWAY_N, IMG_END_RUNAWAY_W, IMG_END_RUNAWAY_H, 0xF81F}, \
    {"emo_success", img_emo_success_frames, IMG_EMO_SUCCESS_N, IMG_EMO_SUCCESS_W, IMG_EMO_SUCCESS_H, 0xF81F}, \
    {"emo_fail", img_emo_fail_frames, IMG_EMO_FAIL_N, IMG_EMO_FAIL_W, IMG_EMO_FAIL_H, 0xF81F}, \
    {"food_0", img_food_0_frames, IMG_FOOD_0_N, IMG_FOOD_0_W, IMG_FOOD_0_H, 0xF81F}, \
    {"food_1", img_food_1_frames, IMG_FOOD_1_N, IMG_FOOD_1_W, IMG_FOOD_1_H, 0xF81F}, \
    {"food_2", img_food_2_frames, IMG_FOOD_2_N, IMG_FOOD_2_W, IMG_FOOD_2_H, 0xF81F}, \
    {"food_3", img_food_3_frames, IMG_FOOD_3_N, IMG_FOOD_3_W, IMG_FOOD_3_H, 0xF81F}, \
    {"food_4", img_food_4_frames, IMG_FOOD_4_N, IMG_FOOD_4_W, IMG_FOOD_4_H, 0xF81F}, \
