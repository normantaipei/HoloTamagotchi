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

// 展開成 ImageAsset 陣列項，供 character.h 的 IMAGES[] 使用。
#define MARINE_IMAGES \
    {"idle", img_idle, IMG_IDLE_W, IMG_IDLE_H, 0xF81F}, \
    {"yawn", img_yawn, IMG_YAWN_W, IMG_YAWN_H, 0xF81F}, \
    {"cheer", img_cheer, IMG_CHEER_W, IMG_CHEER_H, 0xF81F}, \
    {"pet", img_pet, IMG_PET_W, IMG_PET_H, 0xF81F}, \
    {"eat", img_eat, IMG_EAT_W, IMG_EAT_H, 0xF81F}, \
    {"sleep", img_sleep, IMG_SLEEP_W, IMG_SLEEP_H, 0xF81F}, \
    {"egg", img_egg, IMG_EGG_W, IMG_EGG_H, 0xF81F}, \
    {"bg_room", img_bg_room, IMG_BG_ROOM_W, IMG_BG_ROOM_H, 0xFFFF}, \
    {"end_good", img_end_good, IMG_END_GOOD_W, IMG_END_GOOD_H, 0xF81F}, \
    {"end_normal", img_end_normal, IMG_END_NORMAL_W, IMG_END_NORMAL_H, 0xF81F}, \
    {"end_bad", img_end_bad, IMG_END_BAD_W, IMG_END_BAD_H, 0xF81F}, \
    {"end_runaway", img_end_runaway, IMG_END_RUNAWAY_W, IMG_END_RUNAWAY_H, 0xF81F}, \
    {"emo_success", img_emo_success, IMG_EMO_SUCCESS_W, IMG_EMO_SUCCESS_H, 0xF81F}, \
    {"emo_fail", img_emo_fail, IMG_EMO_FAIL_W, IMG_EMO_FAIL_H, 0xF81F}, \
    {"food_0", img_food_0, IMG_FOOD_0_W, IMG_FOOD_0_H, 0xF81F}, \
    {"food_1", img_food_1, IMG_FOOD_1_W, IMG_FOOD_1_H, 0xF81F}, \
    {"food_2", img_food_2, IMG_FOOD_2_W, IMG_FOOD_2_H, 0xF81F}, \
    {"food_3", img_food_3, IMG_FOOD_3_W, IMG_FOOD_3_H, 0xF81F}, \
    {"food_4", img_food_4, IMG_FOOD_4_W, IMG_FOOD_4_H, 0xF81F}, \
