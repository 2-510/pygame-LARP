import pygame
import os
import sys

# -------------------------
# 初始化與設定 (保持不變)
# -------------------------
pygame.init()

try:
    pygame.mixer.init()
except Exception as e:
    print(f"Audio init error: {e}")


width, height = 800, 600
screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
pygame.display.set_caption("武陵高中地圖")
clock = pygame.time.Clock()
FPS = 60

# 顏色
WHITE = (255, 255, 255)
RED = (220, 30, 30)
BLACK = (0, 0, 0)
GRAY = (255, 255, 255)

# 字體設定 (保持不變)
font_path_win = "C:\\Windows\\Fonts\\msjh.ttc"
if os.path.exists(font_path_win):
    font_main = pygame.font.Font(font_path_win, 24)
    font_title = pygame.font.Font(font_path_win, 36)
else:
    try:
        font_main = pygame.font.SysFont("Microsoft JhengHei", 24)
        font_title = pygame.font.SysFont("Microsoft JhengHei", 36)
    except Exception:
        font_main = pygame.font.SysFont(None, 24)
        font_title = pygame.font.SysFont(None, 36)
# vote的字體設定
BASE_FONT_SIZE = 24
BASE_TITLE_SIZE = 36
BASE_WIDTH, BASE_HEIGHT = 800, 600
def get_font(size):
    if os.path.exists(font_path_win):
        return pygame.font.Font(font_path_win, size)
    return pygame.font.SysFont("Microsoft JhengHei", size)
# 載入主要地圖圖片 (省略)
MAP_PATH = os.path.join("img", "WLSH_Map_v2.png")
try:
    background_img = pygame.image.load(MAP_PATH).convert()
    bg_width, bg_height = background_img.get_size()
except pygame.error:
    print(f"Error: 無法載入地圖圖片 '{MAP_PATH}'。請確認檔案是否存在。")
    background_img = pygame.Surface((10000, 10000))
    background_img.fill((100, 100, 100))
    bg_width, bg_height = background_img.get_size()


# 縮放與拖曳初始參數 (保持不變)
scale = min(width / bg_width, height / bg_height)
ZOOM_SPEED = 0.12
SCALE_MIN = 0.05
SCALE_MAX = 8.0
offset_x, offset_y = 0.0, 0.0
dragging = False
last_mouse_pos = None
BASE_PIN_RADIUS = 60


# -------------------------
# 遊戲狀態管理 (全域變數)
# -------------------------
CURRENT_ITEM_INDEX = 0  # 當前道具索引
CURRENT_ITEM_LIST = []  # 當前樓層的道具列表
CURRENT_ITEM_IMAGE = None
current_lines = []
SELECTED_ITEM = None

bell_index = 0
has_played_bell = False  # 全域初始化，防止 NameError
# =========================
# 音效初始化
# =========================
pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()
pygame.mixer.init()

bell1 = pygame.mixer.Sound(os.path.join("audio", "bell1.wav"))
bell2 = pygame.mixer.Sound(os.path.join("audio", "bell2.wav"))
backpack_sound = pygame.mixer.Sound(os.path.join("audio", "backpack.wav"))
bell1.set_volume(0.7)
bell2.set_volume(0.9)
backpack_sound.set_volume(0.7)

# 專用頻道
bell_channel = pygame.mixer.Channel(1)
bell_channel_2 = pygame.mixer.Channel(2)
backpack_channel = pygame.mixer.Channel(3)

BUILDING_8_SOUND_PLAYED = False
has_special_item = False

def play_backpack_sound():
    # 避免重複播放，如果已經在播就不要重播
    if not backpack_channel.get_busy():
        backpack_channel.play(backpack_sound)


#has_special_item = True!!!



def clicked(self, event):
    # 只在滑鼠按下事件且滑鼠在按鈕範圍內才返回 True
    return event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos)
# -------------------------
# 樓層按鈕資料 (省略)
buttons = [
    {"id": "building_1", "name": "活中", "pos": (8000, 7500)},
    {"id": "building_2", "name": "姜姜", "pos": (1000, 7500)},
    {"id": "building_3", "name": "大鏡", "pos": (2950, 7900)},
    {"id": "building_4", "name": "工藝館", "pos": (7000, 3000)},
    {"id": "building_5", "name": "蘊真樓", "pos": (1200, 11000)},
    {"id": "building_6", "name": "美池區", "pos": (5100, 9700)},
    {"id": "building_7", "name": "體育館", "pos": (7200, 5000)},
    {"id": "building_8", "name": "分科鐘", "pos": (2950, 9700)},
    {"id": "building_9", "name": "嘉芳", "pos": (1000, 8000)},
    {"id": "building_10", "name": "電梯", "pos": (3050, 10480)},
]
# -------------------------
# 圖片載入 (省略)
# -------------------------
building_images = {}
for b in buttons:
    bid = b["id"]
    img_path = os.path.join("img", f"{bid}.png")
    if os.path.exists(img_path):
        try:
            building_images[bid] = pygame.image.load(img_path).convert_alpha()
        except pygame.error:
            building_images[bid] = None
    else:
        building_images[bid] = None

NPC_IMAGES = {
    "building_1": {
        1: pygame.image.load("img/活中.jpg").convert_alpha(),
        2: pygame.image.load("img/人物-警衛.png").convert_alpha(),
    },
    "building_2": {
        1: pygame.image.load("img/人物-姜姜.png").convert_alpha(),
        2: pygame.image.load("img/人物-姜姜.png").convert_alpha(),
    },
    "building_3": {
        1: pygame.image.load("img/小美幽靈.png").convert_alpha(),
        2: pygame.image.load("img/小美幽靈.png").convert_alpha(),
    },
    "building_4": {
        1: pygame.image.load("img/人物-小玩具.png").convert_alpha(),
        2: pygame.image.load("img/人物-小玩具.png").convert_alpha(),
    },
    "building_5": {
        1: pygame.image.load("img/人物-肅毅.png").convert_alpha(),
        2: pygame.image.load("img/人物-肅毅.png").convert_alpha(),
    },
    "building_6": {
        1: pygame.image.load("img/人物-蛋蛋.png").convert_alpha(),
        2: pygame.image.load("img/人物-蛋蛋.png").convert_alpha(),
    },
    "building_7": {
        1: pygame.image.load("img/體育館.jpg").convert_alpha(),
        2: pygame.image.load("img/人物-警衛.png").convert_alpha(),
    },
    "building_8": {
        1: pygame.image.load("img/人物-陳宥淇.png").convert_alpha(),
        2: pygame.image.load("img/人物-陳宥淇.png").convert_alpha(),
    },
    "building_9": {
        1: pygame.image.load("img/人物-嘉芳.png").convert_alpha(),
        2: pygame.image.load("img/人物-嘉芳.png").convert_alpha(),
    },
    "building_10": {
        1: pygame.image.load("img/電梯.jpg").convert_alpha(),
        2: pygame.image.load("img/電梯.jpg").convert_alpha(),
    }
}


ITEM_IMAGES = {
    "監視器柏霖": pygame.image.load("img/0.案發前監視器畫面-柏霖.png").convert_alpha(),
    "監視器俊傑": pygame.image.load("img/2.監視器毀損前畫面-俊傑.png").convert_alpha(),
    "監視器嘉琪": pygame.image.load("img/1.案發前監視器畫面-嘉琪.png").convert_alpha(),
    "翻譯蒟蒻": pygame.image.load("img/翻譯蒟蒻.webp").convert_alpha(),

    "嘉琪日記1-1": pygame.image.load("img/嘉琪日記1-第1頁.png").convert_alpha(),
    "嘉琪日記1-2": pygame.image.load("img/嘉琪日記1-第2頁.png").convert_alpha(),
    "馬克杯杯": pygame.image.load("img/馬克杯杯.png").convert_alpha(),
    "驗屍報告": pygame.image.load("img/驗屍報告JPG.png").convert_alpha(),

    "臨時通行證": pygame.image.load("img/臨時通行證.png").convert_alpha(),
    "小美道歉信": pygame.image.load("img/小美道歉信.jpg").convert_alpha(),
    "手鍊": pygame.image.load("img/手鍊.png").convert_alpha(),
    "手電筒": pygame.image.load("img/手電筒.png").convert_alpha(),

    "鎖屏畫面": pygame.image.load("img/鎖屏畫面.webp").convert_alpha(),
    "嘉琪日記2-1": pygame.image.load("img/嘉琪日記2-第1頁.png").convert_alpha(),
    "嘉琪日記2-2": pygame.image.load("img/嘉琪日記2-第2頁.png").convert_alpha(),

    "對話紀錄1": pygame.image.load("img/3.小美柏霖對話紀錄01.png").convert_alpha(),
    "對話紀錄2": pygame.image.load("img/4.小美柏霖對話紀錄02.png").convert_alpha(),

    "奶龍": pygame.image.load("img/奶龍.png").convert_alpha(),





}

#INVENTORY = {"監視器柏霖","監視器嘉琪","監視器俊傑","手電筒", "嘉琪日記","馬克杯杯","鎖屏畫面","手鍊","翻譯蒟蒻","馬克杯杯","手電筒","嘉琪日記1-1","嘉琪日記1-2","嘉琪日記2-1","嘉琪日記2-2","臨時通行證","對話紀錄1","對話紀錄2","驗屍報告",}

# 道具資料按樓層+階段
BUILDING_ITEMS = {
    "building_1": {1: ["手鍊"], 2: ["警衛"]},
    "building_2": {1: [], 2: ["馬克杯杯"]},
    "building_3": {1: ["鎖屏畫面"], 2: ["對話紀錄1","對話紀錄2"]},
    "building_4": {1: [], 2: ["奶龍","驗屍報告"]},
    "building_5": {1: [], 2: ["手電筒"]},
    "building_6": {1: [], 2: []},
    "building_7": {1: [], 2: ["嘉琪日記2-1","嘉琪日記2-2"]},
    "building_8": {1: [], 2: []},
    "building_9": {1: ["翻譯蒟蒻"], 2: []},
    "building_10": {1: ["嘉琪日記1-1","嘉琪日記1-2"], 2: ["小美道歉信"]}


}


# =========================
# 樓層階段進度管理
# =========================

BUILDING_STAGE = {
    "building_1": 1,
    "building_2": 1,
    "building_3": 1,
    "building_4": 1,
    "building_5": 1,
    "building_6": 1,
    "building_7": 1,
    "building_8": 1,
    "building_9": 1,
    "building_10": 1,
}

FLOOR_ITEM_RULES = {
    "building_1": {
        1: {
            "items": ["手鍊"]
        },
    },

    "building_9": {
        1: {
            "items": ["翻譯蒟蒻"]
        },
    },

    "building_10": {
        1: {
            "items": ["嘉琪日記1-1", "嘉琪日記1-2"]
        },
    },
}

KEYWORD_RULES = {

    "building_1": {  # 活中
        1: {
            "next_stage": 2,
            "use_item": "手電筒"
        },
    },

    "building_2": {  # 姜姜
        1: {
            "keywords": ["披薩","pizza","比薩","匹撒"],
            "next_stage": 2,
            "give_item": "馬克杯杯"

        },
    },

    "building_3": {  # 大鏡
        1: {
            "keywords": ["3916",],
            "next_stage": 2,
            "give_item": "4.小美柏霖對話紀錄02",
            "use_item": "手鍊"

        },
    },

    "building_4": {  # 工藝館
        1: {
            "next_stage": 2,
            "use_item": "臨時通行證",
            "give_item": ["驗屍報告"]
        },
    },

    "building_5": {  # 蘊真樓
        1: {
            "keywords": ["2006年3月17日卯時","2006年3月17日 卯時","2006/3/17 卯時","2006/3/17卯時","丙戌年2月18日卯時","丙戌年 2月18日 卯時","丙戌年2月18日 卯時","丙戌年 2月18日卯時","丙戌年二月十八日卯時"],
            "next_stage": 2,
            "give_item": "手電筒"
        },

    },

    "building_6": {  # 美池區
        1: {
            "next_stage": 2,
            "use_item": "翻譯蒟蒻",
        },
    },

    "building_7": {  # 體育館
        1: {

            "next_stage": 2,
            "use_item": "手電筒"
        },
    },

    "building_8": {  # 分科鐘
        1: {
            "keywords": ["郁文", "我是郁文","我愛郁文","郁文是我老闆","與聞","英文老師"],
            "next_stage": 2,
            "give_item": "臨時通行證"
        },
    },


    "building_10": {  # 電梯
        1: {
            "keywords": ["肅毅", "肅毅好帥","肅毅大帥哥","肅毅帥潮","電腦老師好酷"],
            "next_stage": 2,
            "give_item": "小美道歉信"
        },
    }

}


# 對話資料按樓層+階段
ALL_BUILDING_LINES = {
    "building_1": {
        1: ["活中：為了體育不要被當，小美生前賣力的打網球", "活中：結果她的手鍊不小心從網球場飛到活中了"], #手電筒
        2: ["警衛：都這麼晚了，你們怎麼還在學校逗留", "警衛：ㄟ...你們兩個小女生不是同一個社團的嗎?","警衛：我那時候正在巡邏，經過社辦門口，看到你們吵得好兇喔","警衛：聽起來明明也不是什麼大不了的事，幹嘛要吵成那樣呢？","警衛：同學間有什麼事情要好好溝通阿","警衛：大家都是好同學又不是仇人，對吧？" ],
    },
    "building_2": {
        1: ["姜姜：ㄟ同學，要不要參加環島隊阿","姜姜：哎呀，不要也沒關係，但答對謎語才能放你走", "姜姜：假如生活欺騙了你，可以吃什麼呢?"],
        2: ["姜姜：沒想到你竟然知道!","姜姜：對了，這是俊傑燒的馬克杯杯忘記帶走了","姜姜：看在你答對的份上...", "姜姜：我就不當掉俊傑美術了"]
    },
    "building_3": {
        1: ["小美幽靈：我死的好冤...為什麼在那種高度，它還推得下手？", "小美幽靈：這是我的手機，但是密碼想不起來了"],
        2: ["小美幽靈：哎呀!手機竟然成功解鎖了！","小美幽靈：你看到了吧？他根本不愛我！"]
    },
    "building_4": {
        1: ["小玩具：同學我要記你警告，你違反校規囉！"],
        2: ["小玩具：孩子阿，沒想到你們是來調查案件的","小玩具：警察在現場找到了奶龍的吊飾","小玩具：上面沒有雨水淋過的痕跡，表示是案發之後才出現在這裡的","小玩具：還有這裡有一份小美的驗屍報告，或許對你們有幫助。","小玩具：對ㄟ，你們從蘊真樓下樓時，有沒有說些好聽的話呀"]
    },
    "building_5": {
        1: ["肅毅：有料!", "肅毅：你們是不是在追查什麼不該碰的事？除非你有死者的生辰八字，否則我也幫不了你。"],
        2: ["肅毅：(閉目掐指) 2006年3月17日卯時...","肅毅：她是花花庫馬","肅毅：此命主近期紅鸞星動卻遭逢巨變，原本的良緣變成了孽緣。她生命中有一份被深埋的感情，但對方並不是那個與她爭吵的男孩。","肅毅：對了，情人節快到了","肅毅：送你們一個月老拜過的手電筒，或許能幫助你們找到真愛。"],
    },
    "building_6": {
        1: ["蛋蛋：汪汪汪汪汪汪!"],
        2: ["蛋蛋：阿!我終於可以講話了汪","蛋蛋：小美之前常常來餵我吃東西","蛋蛋：聽說她的生日好像快到了汪","蛋蛋：他的八字好像是2006年3月17日卯時吧"]
    },
    "building_7": {
        1: ["體育館：晚上的體育館好恐怖啊...", "體育館：我怕怕"],
        2: ["體育館：你找到了嘉琪日記的另一半！"],
    },
    "building_8": {
        1: ["陳有機：我是你的英文老師。你有聽到這鐘聲嗎？晚上的校園總有些不該聽到的聲音..."],
        2: ["陳有機：原來你知道郁文喔，真巧!","陳有機：我給你一張通行證吧，這樣可以在學校裡能更方便一些","陳有機：搞不好也可以翻牆呢！"]
    },
    "building_9": {
        1: ["佳芳：你說柏霖跟淑芬喔？前天我確實看到他們在校外的咖啡廳。", "佳芳：兩個人湊得很近在看不知道什麼東西，看起來關係不錯耶！","佳芳：欸對了，你想不想吃我剛做好的蒟蒻呢?"],
    },
    "building_10": {
        1: ["電梯：你在角落發現了半本日記..."],
        2: ["電梯：這是夾在小美日記的信件...","電梯：應該是因為頂樓風太大了，所以不小心飛出來了","電梯：蒐證差不多結束了","電梯：看你們可以開始討論找兇手了..."]
    }
}

class FixedIcon:
    """
    固定在螢幕上的功能圖示
    - 位置、大小皆使用比例
    - resize 時自動更新
    """
    def __init__(self, image, x_ratio, y_ratio, size_ratio):
        self.image_orig = image
        self.image = image
        self.x_ratio = x_ratio
        self.y_ratio = y_ratio
        self.size_ratio = size_ratio
        self.rect = pygame.Rect(0, 0, 0, 0)

    def resize(self, width, height):
        size = int(min(width, height) * self.size_ratio)
        x = int(width * self.x_ratio)
        y = int(height * self.y_ratio)
        self.rect = pygame.Rect(x, y, size, size)
        self.image = pygame.transform.smoothscale(
            self.image_orig, (size, size)
        )

    def draw(self, screen):
        screen.blit(self.image, self.rect.topleft)

# =========================
# 背包圖示（比例式）
# =========================
BAG_PATH = pygame.image.load(os.path.join("img", "bag.webp")).convert_alpha()

bag_icon = FixedIcon(
    image=BAG_PATH,
    x_ratio=0.83,    # 靠右
    y_ratio=0.03,    # 靠上
    size_ratio=0.18  # 螢幕短邊 10%
)
# 資料夾路徑
IMG_DIR = "img"

show_shelf = False
UP_PATH = pygame.image.load(os.path.join(IMG_DIR, "置物櫃-按鈕（上）.png")).convert_alpha()
DOWN_PATH = pygame.image.load(os.path.join(IMG_DIR, "置物櫃-按鈕（下）.png")).convert_alpha()
up_button = FixedIcon(image=UP_PATH, x_ratio=0.83, y_ratio=0.3, size_ratio=0.2)
down_button = FixedIcon(image=DOWN_PATH, x_ratio=0.83, y_ratio=0.7, size_ratio=0.2)
bag_shelf_image = pygame.image.load(os.path.join(IMG_DIR, "置物櫃-層架.png")).convert_alpha()
bag_shelf_rect = bag_shelf_image.get_rect()

# 16 個物品圖 + 個別開關
class BagItem:
    def __init__(self, key, image):
        self.key = key
        self.image_orig = image
        self.visible = True  # 個別控制
        self.rect = None
    def resize(self, shelf_x, shelf_y, shelf_w, segment_h, index):
        """根據當前架子與段落計算位置大小"""
        if not self.visible:
            return
        item_h = int(segment_h * 0.5)
        item_w = int(item_h * self.image_orig.get_width() / self.image_orig.get_height())
        item_x = shelf_x + (shelf_w - item_w)//2
        item_y = shelf_y + int((index + 0.5) * segment_h - item_h/2)
        self.rect = pygame.Rect(item_x, item_y, item_w, item_h)
        self.image = pygame.transform.smoothscale(self.image_orig, (item_w, item_h))

    def draw(self, screen):
        if self.visible:
            screen.blit(self.image, self.rect.topleft)
class ItemPreview:
    def __init__(self):
        self.image = None
        self.rect = None
        self.visible = False
        # 新增兩個按鈕
        self.use_button_rect = None
        self.cancel_button_rect = None
        self.use_button_text = "使用"
        self.cancel_button_text = "取消"
        self.use_button_text = "使用"  # 改文字
        self.cancel_button_text = "取消"
        self.current_item = None  # 追蹤目前放大的物品

    def show(self, item_image, width, height):
        """設定要顯示的圖片與位置"""
        self.visible = True
        # 左側放大板寬高佔畫面 40% x 60%
            # 1️⃣ 原圖尺寸
        img_w, img_h = item_image.get_size()

        # 2️⃣ 最大顯示範圍（依螢幕）
        max_w = int(width * 0.84)
        max_h = int(height * 0.84)

        # 3️⃣ 計算等比例縮放倍率
        scale = min(max_w / img_w, max_h / img_h)

        preview_w = int(img_w * scale)
        preview_h = int(img_h * scale)

        # 4️⃣ 高品質等比例縮放
        self.image = pygame.transform.smoothscale(
            item_image,
            (preview_w, preview_h)
        )

        # 5️⃣ 置中顯示
        self.rect = self.image.get_rect(
            center=(width // 2, height // 2)
        )
         # 按鈕寬高
        btn_w, btn_h = int(preview_w*0.35), int(preview_h*0.1)
        btn_gap = 10

        # 使用按鈕
        btn_x = self.rect.x
        btn_y = self.rect.bottom + btn_gap
        self.use_button_rect = pygame.Rect(btn_x, btn_y, btn_w, btn_h)

        # 取消按鈕
        btn_x2 = self.rect.x + btn_w + btn_gap
        btn_y2 = btn_y
        self.cancel_button_rect = pygame.Rect(btn_x2, btn_y2, btn_w, btn_h)

    def hide(self):
        self.visible = False
        self.current_item = None

    def draw(self, screen):
        if self.visible:
            # 放大圖
            screen.blit(self.image, self.rect.topleft)
             # 畫使用按鈕
            pygame.draw.rect(screen, (100,200,100), self.use_button_rect)
            pygame.draw.rect(screen, (0,0,0), self.use_button_rect, 2)

            txt = font_main.render(self.use_button_text, True, (0,0,0))
            screen.blit(txt, txt.get_rect(center=self.use_button_rect.center))

            # 畫取消按鈕
            pygame.draw.rect(screen, (200,100,100), self.cancel_button_rect)
            pygame.draw.rect(screen, (0,0,0), self.cancel_button_rect, 2)
            txt2 = font_main.render(self.cancel_button_text, True, (0,0,0))
            screen.blit(txt2, txt2.get_rect(center=self.cancel_button_rect.center))

item_preview = ItemPreview()


ITEM_KEYS = list(ITEM_IMAGES.keys())

ITEM_ORDER = [
    pygame.image.load(os.path.join(IMG_DIR, "0.案發前監視器畫面-柏霖.png")).convert_alpha(),
    pygame.image.load(os.path.join(IMG_DIR, "1.案發前監視器畫面-嘉琪.png")).convert_alpha(),
    pygame.image.load(os.path.join(IMG_DIR, "2.監視器毀損前畫面-俊傑.png")).convert_alpha(),
    pygame.image.load(os.path.join(IMG_DIR, "翻譯蒟蒻.webp")).convert_alpha(),

    pygame.image.load(os.path.join(IMG_DIR, "嘉琪日記1-第1頁.png")).convert_alpha(),
    pygame.image.load(os.path.join(IMG_DIR, "嘉琪日記1-第2頁.png")).convert_alpha(),
    pygame.image.load(os.path.join(IMG_DIR, "馬克杯杯.png")).convert_alpha(),
    pygame.image.load(os.path.join(IMG_DIR, "驗屍報告JPG.png")).convert_alpha(),

    pygame.image.load(os.path.join(IMG_DIR, "臨時通行證.png")).convert_alpha(),
    pygame.image.load(os.path.join(IMG_DIR, "小美道歉信.jpg")).convert_alpha(),
    pygame.image.load(os.path.join(IMG_DIR, "手鍊.png")).convert_alpha(),
    pygame.image.load(os.path.join(IMG_DIR, "手電筒.png")).convert_alpha(),

]



ITEM_GROUPS = []
group = []

for key in ITEM_KEYS:
    if key in ITEM_IMAGES:
        group.append(BagItem(key, ITEM_IMAGES[key]))

    if len(group) == 4:
        ITEM_GROUPS.append(group)
        group = []

if group:
    ITEM_GROUPS.append(group)




# 先全部隱藏
for group in ITEM_GROUPS:
    for item in group:
        item.visible = False

# 只顯示三個監視器
ITEM_GROUPS[0][0].visible = True   # 柏霖
ITEM_GROUPS[0][1].visible = True   # 嘉琪
ITEM_GROUPS[0][2].visible = True   # 俊傑

current_group_index = 0   # 這一行必須加
# -------------------------
# bag_shelf 畫面函式
# -------------------------
def draw_bag_shelf(screen, width, height):
    global current_group_index
    width, height = screen.get_size()
    gap = int(height * 0.0005)
    btn_w = btn_h = int(bag_icon.rect.width * 0.6)
    # ====== up button ======
    up_button.rect = pygame.Rect(
        bag_icon.rect.centerx - btn_w//2,      # x 對齊 bag 右側
        bag_icon.rect.bottom + gap,           # y 在 bag 下方
        btn_w,
        btn_h
    )
    up_button.image = pygame.transform.smoothscale(
        up_button.image_orig, (btn_w, btn_h)
    )
    # ====== shelf 尺寸 =====
    orig_w, orig_h = bag_shelf_image.get_size()
    scale = height * 0.55 / orig_h     # shelf 高度佔畫面 55%
    shelf_w = int(orig_w * scale)
    shelf_h = int(orig_h * scale)
    shelf_x = bag_icon.rect.centerx - shelf_w//2
    shelf_y = up_button.rect.bottom + gap
    bag_shelf_rect = pygame.Rect(
        bag_icon.rect.centerx - shelf_w//2,
        up_button.rect.bottom + gap,
        shelf_w,
        shelf_h
    )
    bag_shelf_image_scaled = pygame.transform.smoothscale(
        bag_shelf_image, (shelf_w, shelf_h)
    )
    # ====== ② 畫 shelf 本體（在物品下面）======
    screen.blit(
        bag_shelf_image_scaled,
        bag_shelf_rect.topleft
    )
    # ====== down button ======
    down_button.rect = pygame.Rect(
        bag_icon.rect.centerx - btn_w//2,      # x 對齊 bag 右側
        bag_shelf_rect.bottom + gap,
        btn_w,
        btn_h
    )
    down_button.image = pygame.transform.smoothscale(
        down_button.image_orig, (btn_w, btn_h)
    )
    # ====== ① 畫上下按鈕======
    up_button.image = pygame.transform.smoothscale(up_button.image_orig, (btn_w, btn_h))
    down_button.image = pygame.transform.smoothscale(down_button.image_orig, (btn_w, btn_h))

    up_button.draw(screen)
    down_button.draw(screen)

    # ====== ② 最後畫物品（最上層） ======
    items = ITEM_GROUPS[current_group_index]
    segment_h = shelf_h // 4

    for i, item in enumerate(items):
        item.resize(shelf_x, shelf_y, shelf_w, segment_h, i)
        item.draw(screen)

# -------------------------
# 角色卡設定
# -------------------------
MENU_ICON_PATH = pygame.image.load(os.path.join("img", "按鈕-角色卡.png")).convert_alpha()

menu_icon = FixedIcon(
    image = MENU_ICON_PATH,
    x_ratio=0.03,    # 左上
    y_ratio=0.03,
    size_ratio=0.18
)


# 載入角色卡按鈕圖片
CARD_ICON_PATH = [
    pygame.image.load(os.path.join(IMG_DIR, "按鈕-俊傑.png")).convert_alpha(),
    pygame.image.load(os.path.join(IMG_DIR, "按鈕-嘉琪.png")).convert_alpha(),
    pygame.image.load(os.path.join(IMG_DIR, "按鈕-柏霖.png")).convert_alpha(),
    pygame.image.load(os.path.join(IMG_DIR, "按鈕-淑芬.png")).convert_alpha(),
]

# 角色卡圖片
card_images = {
    0: pygame.image.load(os.path.join(IMG_DIR, "身份卡-俊傑.png")).convert_alpha(),
    1: pygame.image.load(os.path.join(IMG_DIR, "身份卡-嘉琪.png")).convert_alpha(),
    2: pygame.image.load(os.path.join(IMG_DIR, "身份卡-柏霖.png")).convert_alpha(),
    3: pygame.image.load(os.path.join(IMG_DIR, "身份卡-淑芬.png")).convert_alpha(),
}
current_card_image = None
# 角色卡按鈕圖示
card_icon_group = []
for i, img in enumerate(CARD_ICON_PATH):
    card_icon = FixedIcon(
        image = img,
        x_ratio=0,      # 先給 0，menu_screen 再排位置
        y_ratio=0,
        size_ratio=0    # menu_screen 會用實際像素
    )
    card_icon.index = i
    card_icon_group.append(card_icon)

def menu_screen(screen, width, height):
    screen.fill((30, 30, 30))
    title = font_title.render("角色卡", True, WHITE)
    screen.blit(title, (width//2 - title.get_width()//2, 100))
    #畫四個按鈕
    for i, icon in enumerate(card_icon_group):
        icon_w = int(width * 0.22)     # 寬度比例
        icon_h = int(height * 0.32)    # 高度比例
        padding = int(width * 0.04)

        row = i // 2
        col = i % 2

        start_x = width // 2 - (icon_w * 2 + padding) // 2
        start_y = height // 2 - (icon_h * 2 + padding) // 2
        x = start_x + col * (icon_w + padding)
        y = start_y + row * (icon_h + padding)

        icon.rect = pygame.Rect(x, y, icon_w, icon_h)
        icon.image = pygame.transform.smoothscale(
            icon.image_orig, (icon_w, icon_h)
        )

        icon.draw(screen)

    # 如果有選中的角色卡，顯示在螢幕中央
    if current_card_image:
        new_w = int(current_card_image.get_width() * 0.8)
        new_h = int(current_card_image.get_height() * 0.8)
        s = pygame.transform.smoothscale(current_card_image, (new_w, new_h))
        card_rect = s.get_rect(center=(width//2, height//2))
        screen.blit(s, card_rect.topleft)
        tip = font_main.render("按 R 鍵關閉角色卡", True, WHITE)
        screen.blit(tip, (width//2 - tip.get_width()//2, height - 80))

vote_icon_img = pygame.image.load("img/按鈕-投票.png").convert_alpha()
vote_icon = FixedIcon(
    image=vote_icon_img,
    x_ratio=0.03,    # 左上
    y_ratio=0.16,
    size_ratio=0.18
)
players = [
    {"name": "嘉琪", "votes": 0, "is_murderer": True},
    {"name": "俊傑", "votes": 0, "is_murderer": False},
    {"name": "淑芬", "votes": 0, "is_murderer": False},
    {"name": "柏霖", "votes": 0, "is_murderer": False},
]

# -------------------- 投票畫面 --------------------
class VoteRow:
    def __init__(self, player, index):
        self.player = player
        self.index = index

    def update_layout(self, screen_width, screen_height):
        scale_w = screen_width / BASE_WIDTH
        scale_h = screen_height / BASE_HEIGHT
        row_y = int(150 * scale_h + self.index * 65 * scale_h)
        btn_size = int(50 * min(scale_w, scale_h))
        offset_x = int(20 * scale_w)

        # 名字固定靠左
        self.name_pos = (int(200 * scale_w), row_y + btn_size//2)

        # 按鈕 rect
        center_x = screen_width // 2 + offset_x
        self.minus_rect = pygame.Rect(center_x - 80 - btn_size//2, row_y, btn_size, btn_size)
        self.plus_rect = pygame.Rect(center_x + 80 - btn_size//2, row_y, btn_size, btn_size)
        self.vote_rect = pygame.Rect(center_x - btn_size//2, row_y, btn_size, btn_size)

        # 字體
        self.font = get_font(max(int(BASE_FONT_SIZE * min(scale_w, scale_h)), 12))

    def draw(self, screen):
        # 名字靠左
        name_txt = self.font.render(self.player["name"], True, BLACK)
        name_rect = name_txt.get_rect()
        name_rect.midleft = self.name_pos
        screen.blit(name_txt, name_rect)

        # - 按鈕
        pygame.draw.rect(screen, (200,200,200), self.minus_rect)
        pygame.draw.rect(screen, BLACK, self.minus_rect, 2)
        minus_txt = self.font.render("-", True, BLACK)
        minus_rect = minus_txt.get_rect(center=self.minus_rect.center)
        screen.blit(minus_txt, minus_rect)

        # 票數
        vote_txt = self.font.render(str(self.player["votes"]), True, BLACK)
        vote_rect = vote_txt.get_rect(center=self.vote_rect.center)
        screen.blit(vote_txt, vote_rect)

        # + 按鈕
        pygame.draw.rect(screen, (200,200,200), self.plus_rect)
        pygame.draw.rect(screen, BLACK, self.plus_rect, 2)
        plus_txt = self.font.render("+", True, BLACK)
        plus_rect = plus_txt.get_rect(center=self.plus_rect.center)
        screen.blit(plus_txt, plus_rect)

class VoteScreen:
    def __init__(self, players):
        self.players = players
        self.rows = [VoteRow(p, i) for i, p in enumerate(players)]
        self.submit_rect_base = pygame.Rect(260, 470, 220, 60)
    def update_layout(self, screen_width, screen_height):
        for row in self.rows:
            row.update_layout(screen_width, screen_height)
        scale_w = screen_width / BASE_WIDTH
        scale_h = screen_height / BASE_HEIGHT
        self.submit_rect = pygame.Rect(
            int(self.submit_rect_base.x * scale_w),
            int(self.submit_rect_base.y * scale_h),
            int(self.submit_rect_base.width * scale_w),
            int(self.submit_rect_base.height * scale_h)
        )
        self.font_title = get_font(max(int(BASE_TITLE_SIZE * min(scale_w, scale_h)), 16))
        self.font_main = get_font(max(int(BASE_FONT_SIZE * min(scale_w, scale_h)), 12))

    def total_votes(self):
        return sum(p["votes"] for p in self.players)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            for row in self.rows:
                if row.plus_rect.collidepoint((mx,my)) and row.player["votes"] < 4 and self.total_votes() < 4:
                    row.player["votes"] += 1
                if row.minus_rect.collidepoint((mx,my)) and row.player["votes"] > 0:
                    row.player["votes"] -= 1
            if self.total_votes() == 4 and self.submit_rect.collidepoint((mx,my)):
                return "SUBMIT"

    def draw(self, screen):
        # 標題
        title = self.font_title.render("投票：誰是兇手？", True, BLACK)
        title_rect = title.get_rect(center=(screen.get_width()//2, int(80*screen.get_height()/BASE_HEIGHT)))
        screen.blit(title, title_rect)

        # 投票列
        for row in self.rows:
            row.draw(screen)

        # 總票數
        total_txt = self.font_main.render(f"總票數：{self.total_votes()} / 4", True, BLACK)
        total_rect = total_txt.get_rect(center=(screen.get_width()//2, int(430*screen.get_height()/BASE_HEIGHT)))
        screen.blit(total_txt, total_rect)

        # 送出按鈕
        if self.total_votes() == 4:
            pygame.draw.rect(screen, (180,220,180), self.submit_rect)
            pygame.draw.rect(screen, BLACK, self.submit_rect, 2)
            submit_txt = self.font_main.render("送出投票結果", True, BLACK)
            submit_rect = submit_txt.get_rect(center=self.submit_rect.center)
            screen.blit(submit_txt, submit_rect)

    def check_result(self):
        for p in self.players:
            if p["is_murderer"] and p["votes"] >= 3:
                return "GOOD_END"
        return "BAD_END"

# -------------------- 結局畫面 --------------------
class EndingScreen:
    def __init__(self,screen,text):
        self.screen = screen
        self.text = text
        self.base_width,self.base_height = 800,600
        self.button_rect_base = pygame.Rect(300,500,200,60)

    def update_layout(self, wcreen_width, hscreen_height):
        w,h = self.screen.get_size()
        scale_w = w/self.base_width
        scale_h = h/self.base_height
        self.font_title = get_font(max(int(BASE_TITLE_SIZE*min(scale_w,scale_h)),16))
        self.font_button = get_font(max(int(BASE_FONT_SIZE*min(scale_w,scale_h)),12))
        self.button_rect = pygame.Rect(
            int(self.button_rect_base.x*scale_w),
            int(self.button_rect_base.y*scale_h),
            int(self.button_rect_base.width*scale_w),
            int(self.button_rect_base.height*scale_h)
        )

    def draw(self):
        self.screen.fill(WHITE)
        # 文字
        title_txt = self.font_title.render(self.text,True,BLACK)
        title_rect = title_txt.get_rect(center=(self.screen.get_width()//2,self.screen.get_height()//3))
        self.screen.blit(title_txt,title_rect)
        # 按鈕
        pygame.draw.rect(self.screen,(180,220,180),self.button_rect)
        pygame.draw.rect(self.screen,BLACK,self.button_rect,2)
        btn_txt = self.font_button.render("查看後續",True,BLACK)
        self.screen.blit(btn_txt,btn_txt.get_rect(center=self.button_rect.center))

    def handle_event(self,event):
        if event.type==pygame.MOUSEBUTTONDOWN:
            if self.button_rect.collidepoint(event.pos):
                return "FINAL"

# -------------------- 分頁最終結局 --------------------
class FinalEndingScreen:
    def __init__(self,screen):
        self.screen = screen
        self.text_lines = [
            "小美、柏霖和俊傑從小是青梅竹馬。",
            "",
            "國中時，小美和淑芬是同班同學，兩人原本關係很好。",
            "但某天淑芬誤會小美在背後說她壞話。兩人因此決裂。",
            "然而，小美認為只是無心的開玩笑。",
            "",
            "升上高中後，小美和柏霖交往，且和嘉琪成為好朋友。",
            "因為朝夕相處，嘉琪被小美的魅力吸引，無法自拔地喜歡上了最好的朋友。",
            "嘉琪的暗戀情愫無法對任何人坦城，只好向日記傾訴。",
            "",
            "高二時，嘉琪在社團認識了淑芬。",
            "淑芬勸嘉琪盡早遠離小美，但嘉琪卻處處維護小美",
            "兩人因此產生摩擦。",
            "淑芬甚至開始帶頭排擠嘉琪。",
            "",
            "嘉琪曾多次向小美抱怨淑芬的惡意霸凌。",
            "也從小美口中得知，小美與淑芬有宿怨。",
            "但小美從未為嘉琪出面，也不願透漏從前的恩怨。",
            "",
            "嘉琪因此感到失望又憤怒。",
            "兩人的關係開始出現裂痕。",
            "",
            "暗戀嘉琪的俊傑注意到了這一切。他開始默默觀察一切。",
            "",

            "案發前一周",
            "小美和柏霖分手，小美想討回借出的錢，因此兩人多次爭吵。",
            "",
            "案發前兩天",
            "小美在校外撞見柏霖和淑芬在咖啡廳。"
            "她懷疑柏霖是因為淑芬才急著分手。",
            "但事實上，兩人只是討論讀書會作業。",
            "",
            "案發前 2 小時（下午 4:00）",
            "淑芬在社團集會結束後擋住嘉琪並出言挑釁。",
            "小美向柏霖催討借出的錢。",
            "",
            "",
            "案發前 1.5 小時（下午 4:30）",
            "淑芬長期的霸凌讓嘉琪幾乎難以承受，希望找小美談談，但小美覺得麻煩想要逃避。",
            "淑芬聽說小美和柏霖曾經交往，自己竟然在不知情的情況下和柏霖單獨見面多次",
            "，而有些生氣。",
            "",
            "案發前約 1 小時（下午 5:00）",
            "小美為了避免和嘉琪講話，打算在放學後盡快離開教室，",
            "但想起柏霖要來找她，於是請俊傑幫忙向柏霖轉達她已經提前離開。",
            "嘉琪注意到小美和俊傑說話，想知道是什麼事而跑去問俊傑，",
            "但俊傑不想捲入兩人的紛爭中，沒有透漏小美交代他的事。",
            "柏霖沒有找到小美，只好先和淑芬一起去參加讀書會。",
            "",
            "案發前 30 分鐘（下午 5:30）",
            "嘉琪在自習教室等待，但小美反常的遲遲未出現，",
            "嘉琪覺得小美在迴避她而更生氣，下定決心一定要把事情講清楚。",
            "讀書會下課後，柏霖邀淑芬一起吃晚餐，淑芬不想被誤會於是拒絕。",
            "淑芬在操場遇到俊傑，兩人寒暄幾句後俊傑就上樓拿東西了。",
            "",
            "案發前約 15 分鐘（下午 5:45）",
            "俊傑收拾完書包，帶著排球打算再去操場。",
            "他邊走邊玩球，在路過擊磬堂的樓梯轉角時不小心把球打得太高，砸壞了監視器。",
            "正當俊傑站在原地不知所措時，拿完東西準備下樓的柏霖撞見了這一切，",
            "心虛的他連忙跑走，並沒有看清對方是誰。",
            "",
            "案發前 10 分鐘（下午 5:50）",
            "柏霖在樓梯口附近徘徊一段時間，拍下監視器毀損的照片，打算晚點再回報給學務處。",
            "淑芬上樓拿東西時遇到小美。",
            "嘉琪來到擊磬堂，開始回想被霸凌的經過，情緒更加激動。",
            "",
            "案發當下（約下午 6:00）",
            "小美對嘉琪抱怨的事避重就輕，讓嘉琪很不滿，兩人爆發激烈爭執。",
            "嘉琪情緒激動之下出手推了小美，小美失足墜樓。",
            "",
            "案發後 5 分鐘（下午6:05）",
            "在操場打球的俊傑看到人群聚集在崇德樓下，好奇的跑去圍觀，卻發現是小美墜樓。",
            "震驚的同時發現嘉琪躲在遠處偷看。",
            "",
            "案發隔天",
            "擊磬堂被封鎖調查。監視器壞掉的時間剛好避開關鍵畫面。",
            "學校召集當天的目擊者調查，以小美是自殺結案。",
            ""
            "真相被說出口的那一刻，死寂瀰漫整個校園。",
            "擊磬堂沒有再出現怪聲，大鏡附近的異象、小美的影子也全都煙消雲散。",
            "",
            "有些事情，終於被聽見了。",
            "",
            "嘉琪很快被帶離學校，留下教室裡空缺的座位和校園中四竄的傳言。",
            "她也接受了該承擔的一切。",
            "幾年後，有人說在某個城市的書店見過她。",
            "她坐在窗邊，看漫畫、喝咖啡，偶爾在筆記本上寫東西。",
            "",
            "淑芬在真相揭開後，心神恍惚了數天，卻不是因為命案。",
            "那封國中時期、被反覆塗改的道歉信，像一顆遲來的石子，丟進她以為早已乾涸的湖。",
            "她沒有原諒小美，卻也不再恨她和嘉琪了。",
            "她努力的回到原本的生活，以成為化學老師為目標努力著。",
            "",
            "俊傑一直覺得，那顆砸壞監視器的球，像是他人生中最準的一次失誤。",
            "那晚過後他依然是班上同學信任的班長。",
            "偶爾他會和嘉琪聯絡，但在同學們面前絕口不提她的事。",
            "後來他因緣際會下成為歌手，希望把當時的經歷唱出來。",
            "",
            "柏霖一畢業就離開了這座城市。",
            "他很少再提起小美，但偶爾和俊傑見面時，還是會想起兒時三人一起玩的回憶。",
            "後來他也再談過幾段感情，但都無疾而終。",
            "現在的他希望透過從政去幫助如他們當時一樣掙扎著的青少年們。",
            "",
            "沒有人知道，小美最後留下的是不是怨念。",
            "但可以確認的是，她也留下一些零碎的東西：",
            "沒寄出的信、沒說完的話，還有那些「其實我也很害怕」的瞬間。",
            "",
            "學生們重新回到擊磬堂活動，當時的事已被淡忘，像是只存在學生的閒談中。",
            "",
            "故事結束了。",
            "但他們的人生，還在繼續。"
        ]
        self.base_width,self.base_height = 800,600
        self.current_page = 0
        self.lines_per_page = 12
        self.button_rect_base = pygame.Rect(300,500,200,60)

    def update_layout(self, screen_width, screen_height):
        w,h = self.screen.get_size()
        scale_w = w/self.base_width
        scale_h = h/self.base_height
        self.font = get_font(max(int(20*min(scale_w,scale_h)),12))
        self.line_height = int(28*scale_h)
        self.start_y = int(50*scale_h)
        self.button_rect = pygame.Rect(
            int(self.button_rect_base.x*scale_w),
            int(self.button_rect_base.y*scale_h),
            int(self.button_rect_base.width*scale_w),
            int(self.button_rect_base.height*scale_h)
        )

    def draw(self):
        self.screen.fill(WHITE)
        start_line = self.current_page*self.lines_per_page
        end_line = start_line+self.lines_per_page
        page_lines = self.text_lines[start_line:end_line]

        y = self.start_y
        for line in page_lines:
            txt = self.font.render(line,True,BLACK)
            self.screen.blit(txt,(50,y))
            y+=self.line_height

        btn_text = "下一頁" if end_line<len(self.text_lines) else "結束遊戲"
        pygame.draw.rect(self.screen,(180,220,180),self.button_rect)
        pygame.draw.rect(self.screen,BLACK,self.button_rect,2)
        btn_txt = self.font.render(btn_text,True,BLACK)
        self.screen.blit(btn_txt,btn_txt.get_rect(center=self.button_rect.center))

    def handle_event(self,event):
        if event.type==pygame.MOUSEBUTTONDOWN:
            if self.button_rect.collidepoint(event.pos):
                start_line = self.current_page*self.lines_per_page
                end_line = start_line+self.lines_per_page
                if end_line<len(self.text_lines):
                    self.current_page+=1
                else:
                    pygame.quit()
                    sys.exit()


vote_screen = VoteScreen(players)
good_screen = EndingScreen(screen,"成功找對兇手了!!! 兇手就是 - 嘉琪!!!!")
bad_screen  = EndingScreen(screen,"你沒找到兇手...... 兇手是 - 嘉琪!!!!")
final_screen = FinalEndingScreen(screen)



# -------------------------
# UI 元件類別 (省略所有 class 定義，假設它們在實際文件中存在且正確)
# -------------------------
class InputBox:
    def __init__(self, font): self.font = font; self.text = ""; self.composition = ""; self.rect = pygame.Rect(0, 0, 0, 0); self.active = True
    def update_text_surface(self): return self.font.render(self.text + self.composition, True, BLACK)
    def resize(self, w, h):
        self.rect = pygame.Rect(int(w * 0.05), int(h * 0.8), int(w * 0.9), int(h * 0.15))
        if self.active: pygame.key.set_text_input_rect(self.rect)
    def handle_event(self, event):
        msg = None
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN: msg = self.text + self.composition; self.text = ""; self.composition = ""
            elif event.key in (pygame.K_BACKSPACE, pygame.K_DELETE):
                if self.composition:
                    self.composition = self.composition[:-1]
                else:
                    self.text = self.text[:-1]
        elif event.type == pygame.TEXTINPUT and self.active: self.text += event.text; self.composition = ""
        elif event.type == pygame.TEXTEDITING and self.active: self.composition = event.text
        return msg
    def draw(self, screen): # ... (繪製程式碼省略) ...
        pygame.draw.rect(screen, WHITE, self.rect)
        pygame.draw.rect(screen, BLACK, self.rect, 2)
        txt_surface = self.update_text_surface()
        text_x = self.rect.x + 10; text_y = self.rect.y + 10
        if txt_surface.get_width() > self.rect.width - 20:
            offset_x = self.rect.width - 20 - txt_surface.get_width()
            temp_surface = pygame.Surface((self.rect.width - 20, self.rect.height - 20), pygame.SRCALPHA)
            temp_surface.blit(txt_surface, (offset_x, 0))
            screen.blit(temp_surface, (text_x, text_y))
        else:
            screen.blit(txt_surface, (text_x, text_y))
        if self.active and not self.composition:
            cursor_surf = self.font.render(self.text, True, BLACK)
            cursor_x = self.rect.x + 10 + cursor_surf.get_width()
            if cursor_surf.get_width() > self.rect.width - 20: cursor_x = self.rect.right - 10
            pygame.draw.line(screen, BLACK, (cursor_x, self.rect.y + 5), (cursor_x, self.rect.bottom - 5), 2)
#道具
class ImageSlot:
    def __init__(self, x_ratio, y_ratio, size_ratio):
        self.x_ratio = x_ratio; self.y_ratio = y_ratio; self.size_ratio = size_ratio; self.rect = pygame.Rect(0, 0, 0, 0); self.image = None
    def resize(self, width, height):
        size = int(min(width, height) * self.size_ratio)
        self.rect = pygame.Rect(int(width * self.x_ratio), int(height * self.y_ratio), size, size)
        if self.image: self.image = pygame.transform.smoothscale(self.image, (size, size))
    def set_image(self, img_surface):
        self.image = img_surface
        if self.image: self.image = pygame.transform.smoothscale(self.image, (self.rect.width, self.rect.height))
    def draw(self, screen):
        pygame.draw.rect(screen, (255, 255, 255), self.rect, 2)
        if self.image: screen.blit(self.image, self.rect.topleft)

class NPCDialog:
    def __init__(self, font): self.font = font; self.text = ""; self.rect = pygame.Rect(0, 0, 0, 0)
    def resize(self, width, height): self.rect = pygame.Rect(int(width * 0.05), int(height * 0.65), int(width * 0.9), int(height * 0.15))
    def set_text(self, text): self.text = text
    def draw(self, screen): # ... (繪製程式碼省略) ...
        pygame.draw.rect(screen, (255, 255, 255), self.rect)
        pygame.draw.rect(screen, (0, 0, 0), self.rect, 2)
        y = self.rect.y + 10
        for line in self.wrap_text(self.text, self.rect.width - 20):
            surf = self.font.render(line, True, (0, 0, 0))
            screen.blit(surf, (self.rect.x + 10, y))
            y += surf.get_height() + 4
    def wrap_text(self, text, max_width):
        lines = []; current = ""
        for char in text:
            test = current + char
            if self.font.size(test)[0] <= max_width: current = test
            else: lines.append(current); current = char
        lines.append(current)
        return lines

class Button:
    def __init__(self, text, font):
        self.text = text; self.font = font; self.x_ratio = 0.82; self.y_ratio = 0.88; self.w_ratio = 0.15; self.h_ratio = 0.07; self.rect = pygame.Rect(0, 0, 0, 0)
    def resize(self, width, height): self.rect = pygame.Rect(int(width * self.x_ratio), int(height * self.y_ratio), int(width * self.w_ratio), int(height * self.h_ratio))
    def clicked(self, event): return event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos)
    def draw(self, screen): # ... (繪製程式碼省略) ...
        pygame.draw.rect(screen, (100, 100, 100), self.rect)
        pygame.draw.rect(screen, (255, 255, 255), self.rect, 2)
        txt = self.font.render(self.text, True, (255, 255, 255))
        screen.blit(txt, txt.get_rect(center=self.rect.center))


# 實例化 UI 元件
npc_slot = ImageSlot(0.05, 0.05, 0.55)
item_slot = ImageSlot(0.5, 0.05, 0.65)
next_button = Button("下一句 ", font_main)
next_item_button = Button("下個道具", font_main)
input_box = InputBox(font_main)
npc_dialog = NPCDialog(font_main)

# 全域變數初始化 (使用預設值)
npc_index = 0
dialog_locked = False
if current_lines:
    npc_dialog.set_text(current_lines[npc_index])
    if current_lines:
        npc_dialog.set_text(current_lines[npc_index])


# -------------------------
# 遊戲邏輯函式 (省略 get_building_lines 內容，保持原樣)
# -------------------------
def get_building_lines(building_id):
    """
    根據 BUILDING_STAGE[building_id]，
    回傳該樓層當前階段的 NPC 對話陣列
    """
    stage = BUILDING_STAGE.get(building_id, 1)

    building_data = ALL_BUILDING_LINES.get(building_id)
    if not building_data:
        return ["（這裡暫時沒有任何人）"]

    lines = building_data.get(stage)

    if not lines:
        return ["NPC：……（目前沒有新的線索）"]

    return lines

#===========================
# 嘗試使用道具推進 NPC 階段
def try_use_item(item_key):
    building = current_screen              # 目前所在樓層
    stage = BUILDING_STAGE[building]        # 目前 NPC 階段
    rule = KEYWORD_RULES.get(building, {}).get(stage)

    if not rule:
        return  # 此樓層此階段不接受使用道具

    if rule.get("use_item") != item_key:
        return  # 道具不對

    # ✅ 條件全對 → 推進 NPC
    next_stage = rule.get("next_stage")
    if next_stage:
        BUILDING_STAGE[building] = next_stage

    # 如果有給道具，也自動取得
    give_items = rule.get("give_item")
    if give_items:
        if isinstance(give_items, str):
            gain_item(give_items)
        elif isinstance(give_items, list):
            for it in give_items:
                gain_item(it)

    # 檢查階段道具獎勵
    check_floor_item_reward(building, BUILDING_STAGE[building])

    # 更新對話文字
    lines = get_building_lines(building)
    npc_dialog.set_text(lines[0] if lines else "")


#===========================
def gain_item(item_key):
    """
    獲得道具，將對應的 BagItem 設為可見
    """
    found = False
    for group in ITEM_GROUPS:
        for item in group:
            if item.key == item_key:
                if not item.visible:
                    item.visible = True
                    print(f"獲得道具：{item_key}")
                found = True
                break
        if found:
            break
#===========================
def unlock_item(item_key):
    global current_group_index

    for gi, group in enumerate(ITEM_GROUPS):
        for item in group:
            if item.key == item_key:
                item.visible = True
                current_group_index = gi   # 自動切到該頁
                print(f"[UNLOCK] {item_key} in group {gi}")
                return

    print(f"[WARN] 找不到道具：{item_key}")


#===========================
# 樓層道具獎勵檢查函式
def check_floor_item_reward(building_id, stage):
    rules = FLOOR_ITEM_RULES.get(building_id, {})
    rule = rules.get(stage)

    if not rule:
        return

    for item_key in rule.get("items", []):
        gain_item(item_key)




# =========================
# 樓層繪圖函式統一
# =========================
def common_building_draw(screen, building_id, building_name, width, height):
    global CURRENT_ITEM_IMAGE, CURRENT_ITEM_LIST, CURRENT_ITEM_INDEX
    global npc_index, current_lines, dialog_locked

    screen.fill(GRAY)
    stage = BUILDING_STAGE[building_id]

    # ===== 對話 =====
    new_lines = get_building_lines(building_id)
    if new_lines != current_lines:
        current_lines = new_lines
        npc_index = 0
        dialog_locked = False
        npc_dialog.set_text(current_lines[0])

    # ===== NPC 圖片 =====
    img = NPC_IMAGES.get(building_id, {}).get(stage)
    npc_slot.set_image(img)
    npc_slot.draw(screen)

    # ===== 道具 =====
    CURRENT_ITEM_LIST = BUILDING_ITEMS.get(building_id, {}).get(stage, [])
    if CURRENT_ITEM_LIST:
        CURRENT_ITEM_INDEX %= len(CURRENT_ITEM_LIST)
        item_key = CURRENT_ITEM_LIST[CURRENT_ITEM_INDEX]
        CURRENT_ITEM_IMAGE = ITEM_IMAGES.get(item_key)
        item_slot.set_image(CURRENT_ITEM_IMAGE)
    else:
        CURRENT_ITEM_IMAGE = None
        item_slot.set_image(None)

    item_slot.draw(screen)

    # ===== UI =====
    npc_slot.draw(screen)
    item_slot.draw(screen)
    npc_dialog.draw(screen)
    input_box.draw(screen)
    # Button positioning update
    # Next Line Button
    next_button.rect.width = npc_dialog.rect.width // 8
    next_button.rect.height = npc_dialog.rect.height // 3
    next_button.rect.x = npc_dialog.rect.right - next_button.rect.width
    next_button.rect.y = npc_dialog.rect.bottom - next_button.rect.height

    # Next Item Button
    next_item_button.rect.width = next_button.rect.width*1.2
    next_item_button.rect.height = next_button.rect.height
    next_item_button.rect.x = next_button.rect.x
    next_item_button.rect.y = next_button.rect.y - next_item_button.rect.height - 10

    next_button.draw(screen)
    next_item_button.draw(screen)


# =========================
# 每個樓層函式
# =========================
def building_1(screen, font, width, height): common_building_draw(screen, "building_1", "活中", width, height)
def building_2(screen, font, width, height): common_building_draw(screen, "building_2", "美育館姜姜", width, height)
def building_3(screen, font, width, height): common_building_draw(screen, "building_3", "大鏡", width, height)
def building_4(screen, font, width, height): common_building_draw(screen, "building_4", "工藝館", width, height)
def building_5(screen, font, width, height): common_building_draw(screen, "building_5", "蘊真樓", width, height)
def building_6(screen, font, width, height): common_building_draw(screen, "building_6", "美池區", width, height)
def building_7(screen, font, width, height): common_building_draw(screen, "building_7", "體育館", width, height)
def building_8(screen, font, width, height): common_building_draw(screen, "building_8", "分科鐘", width, height)
def building_9(screen, font, width, height): common_building_draw(screen, "building_9", "美育館佳芳", width, height)
def building_10(screen, font, width, height): common_building_draw(screen, "building_10", "電梯", width, height)


# -------------------------
# 畫面狀態與 UI 調整
# -------------------------
current_screen = "map"
current_card_image = None
selected_building = None

def resize_ui(width, height):
    input_box.resize(width, height)
    npc_dialog.resize(width, height)
    npc_slot.resize(width, height)
    item_slot.resize(width, height)
    next_button.resize(width, height)
    next_item_button.resize(width, height)

    bag_icon.resize(width, height)
    menu_icon.resize(width, height)
    vote_icon.resize(width, height)
    pygame.key.start_text_input()

resize_ui(width, height)

# -------------------------
# 主迴圈
# -------------------------
running = True
while running:
    clock.tick(FPS)
    events = pygame.event.get()
    previous_screen = current_screen

    for event in events:
        if event.type == pygame.QUIT:
            running = False

        # 處理縮放調整
        elif event.type == pygame.VIDEORESIZE:
            width, height = event.size
            screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
            resize_ui(width, height)
         # 背包圖示點擊切換
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if bag_icon.rect.collidepoint(event.pos):
                    show_shelf = not show_shelf
                    if show_shelf:
                        play_backpack_sound()
            if show_shelf:
                # 1. 檢查放大板使用按鈕
                if item_preview.visible and item_preview.use_button_rect.collidepoint(event.pos):


                    building = current_screen
                    stage = BUILDING_STAGE[building]

                    # 查這一關有沒有「使用道具」規則
                    rule = KEYWORD_RULES.get(building, {}).get(stage)

                    try_use_item(SELECTED_ITEM.key)
                    item_preview.hide()

                if item_preview.visible and item_preview.cancel_button_rect.collidepoint(event.pos):
                    item_preview.hide()

                # 2. 檢查背包物品
                else:
                    items = ITEM_GROUPS[current_group_index]
                    for item in items:
                        if item.rect and item.rect.collidepoint(event.pos):
                            item_preview.current_item = item
                            item_preview.show(item.image_orig, *screen.get_size())
                            SELECTED_ITEM = item
                            break
                    if up_button.rect.collidepoint(event.pos):
                        current_group_index = (current_group_index - 1) % 3
                    elif down_button.rect.collidepoint(event.pos):
                        current_group_index = (current_group_index + 1) % 3

        if current_screen == "map":
            # 地圖事件處理
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    dragging = True
                    last_mouse_pos = event.pos
                    mx, my = event.pos
                    # 使用 MENU_rect 來判斷點擊角色卡按鈕
                    if menu_icon.rect.collidepoint((mx, my)):
                        current_screen = "menu"
                    if vote_icon.rect.collidepoint(event.pos):
                        current_screen = "VOTE"
                    for b in buttons:
                        bx, by = b["pos"]
                        sx = offset_x + bx * scale
                        sy = offset_y + by * scale
                        if (mx - sx) ** 2 + (my - sy) ** 2 <= (BASE_PIN_RADIUS * scale) ** 2:
                            current_screen = b["id"] # 你原本判斷的樓層
                            building_id = b["id"]  # 你原本判斷的樓層
                            selected_building = b["name"]
                            check_floor_item_reward(
                                current_screen,
                                BUILDING_STAGE[current_screen]
                            )
                            if current_screen == "building_8" and not BUILDING_8_SOUND_PLAYED:
                                bell_channel.play(bell1)

                                # 只有拿到其他道具才播第二個
                                if has_special_item:
                                    bell_channel.queue(bell2)  # 等第一個播完自動接

                                BUILDING_8_SOUND_PLAYED = True
                            #if current_screen == "building_10":


                            # --- 這裡必須補上初始化 ---
                            current_lines = get_building_lines(current_screen) # 抓取該地對話
                            npc_index = 0                                     # 索引歸零
                            if current_lines:
                                if current_lines:
                                    if current_lines:
                                        npc_dialog.set_text(current_lines[npc_index])
                            # -----------------------
                            dragging = False
                            last_mouse_pos = None

                            # 💥 修正點 1: 進入樓層時，確保重置全域變數
                            npc_index = 0
                            dialog_locked = False
                            break
                # (縮放、拖曳邏輯不變，省略)
                elif event.button == 4:
                    mx, my = event.pos; cx = (mx - offset_x) / scale; cy = (my - offset_y) / scale; scale *= (1 + ZOOM_SPEED)
                    scale = min(scale, SCALE_MAX); offset_x = mx - cx * scale; offset_y = my - cy * scale
                elif event.button == 5:
                    mx, my = event.pos; cx = (mx - offset_x) / scale; cy = (my - offset_y) / scale; scale /= (1 + ZOOM_SPEED)
                    scale = max(scale, SCALE_MIN); offset_x = mx - cx * scale; offset_y = my - cy * scale

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1: dragging = False; last_mouse_pos = None
            elif event.type == pygame.MOUSEMOTION:
                if dragging and last_mouse_pos is not None:
                    dx = event.pos[0] - last_mouse_pos[0]; dy = event.pos[1] - last_mouse_pos[1]
                    offset_x += dx; offset_y += dy; last_mouse_pos = event.pos

        else: # 樓層畫面
            # 退出樓層
            if current_screen == "VOTE":
                result = vote_screen.handle_event(event)
                if result == "SUBMIT":
                    ending = vote_screen.check_result()
                    current_screen = "GOOD" if ending == "GOOD_END" else "BAD"
            elif current_screen in ["GOOD","BAD"]:
                    result = good_screen.handle_event(event) if current_screen=="GOOD" else bad_screen.handle_event(event)
                    if result=="FINAL":
                        current_screen="FINAL"
            elif current_screen=="FINAL":
                    final_screen.handle_event(event)
            if current_screen == "menu":
              # 角色卡畫面處理
                for icon in card_icon_group:
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        if icon.rect.collidepoint(event.pos):
                            current_card_image = card_images[icon.index]
                if current_card_image:
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                        current_card_image = None
            # 退出樓層
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                # ★ 如果現在正在 building_8，就停聲音
                if current_screen == "building_8":
                    bell_channel.stop()
                    BUILDING_8_SOUND_PLAYED = False

                current_screen = "map"
                npc_dialog.set_text("")
                # 💥 修正點 2: 退出樓層時，確保重置全域變數
                npc_index, dialog_locked = 0, False
                dialog_locked = False

            # 玩家輸入處理
            msg = input_box.handle_event(event)
            if msg:
                msg = msg.strip()
                stage = BUILDING_STAGE[current_screen]
                rule = KEYWORD_RULES.get(current_screen, {}).get(stage)

                if rule:
                    if any(kw in msg for kw in rule["keywords"]):
                        BUILDING_STAGE[current_screen] = rule["next_stage"]

                        # 給道具
                        if "give_item" in rule:
                            gain_item(rule["give_item"])
                            if isinstance(gain_item, list):
                                for item_key in gain_item:
                                    unlock_item(item_key)
                            else:
                                unlock_item(gain_item)

                        current_lines = get_building_lines(current_screen)
                        npc_index = 0
                        npc_dialog.set_text(current_lines[0])


                    else:
                        npc_dialog.set_text("NPC：你說的還不夠關鍵。")
                else:
                    npc_dialog.set_text("NPC：這裡暫時沒有新的線索。")


            # 下一句
            if next_button.clicked(event):
                if current_lines:
                    npc_index = (npc_index + 1) % len(current_lines)
                    if current_lines:
                        if current_lines:
                            npc_dialog.set_text(current_lines[npc_index])
            # 道具切換按鈕
            if next_item_button.clicked(event):
               if CURRENT_ITEM_LIST: # 只有列表有東西時才執行
                    CURRENT_ITEM_INDEX = (CURRENT_ITEM_INDEX + 1) % len(CURRENT_ITEM_LIST)
                    item_key = CURRENT_ITEM_LIST[CURRENT_ITEM_INDEX]
                    CURRENT_ITEM_IMAGE = ITEM_IMAGES.get(item_key)
    # -------------------------
    # 繪製畫面內容 (保持不變)
    # -------------------------
    screen.fill(WHITE)

    if current_screen == "map":
        # 地圖繪製邏輯 (省略)
        scaled_w = int(bg_width * scale); scaled_h = int(bg_height * scale)
        scaled_bg = pygame.transform.smoothscale(background_img, (scaled_w, scaled_h))

        if scaled_w <= width: offset_x = (width - scaled_w) // 2
        else: offset_x = min(0, max(offset_x, width - scaled_w))

        if scaled_h <= height: offset_y = (height - scaled_h) // 2
        else: offset_y = min(0, max(offset_y, height - scaled_h))

        screen.blit(scaled_bg, (int(offset_x), int(offset_y)))

        for b in buttons:
            bx, by = b["pos"]; sx = offset_x + bx * scale; sy = offset_y + by * scale
            pygame.draw.circle(screen, RED, (int(sx), int(sy)), max(6, int(BASE_PIN_RADIUS * scale)))

        menu_icon.draw(screen)  # 畫角色卡圖示
        vote_icon.draw(screen)  # 畫投票圖示

    else:
        # 樓層畫面 (調用 common_building_draw)
        if current_screen == "building_1": building_1(screen, font_main, width, height)
        elif current_screen == "building_2": building_2(screen, font_main, width, height)
        elif current_screen == "building_3": building_3(screen, font_main, width, height)
        elif current_screen == "building_4": building_4(screen, font_main, width, height)
        elif current_screen == "building_5": building_5(screen, font_main, width, height)
        elif current_screen == "building_6": building_6(screen, font_main, width, height)
        elif current_screen == "building_7": building_7(screen, font_main, width, height)
        elif current_screen == "building_8": building_8(screen, font_main, width, height)
        elif current_screen == "building_9": building_9(screen, font_main, width, height)
        elif current_screen == "building_10": building_10(screen, font_main, width, height)
        elif current_screen == "menu": menu_screen(screen, width, height)
        elif current_screen=="VOTE":
            vote_screen.update_layout(*screen.get_size())
            vote_screen.draw(screen)
        elif current_screen=="GOOD":
            good_screen.update_layout(*screen.get_size())
            good_screen.draw()
        elif current_screen=="BAD":
            bad_screen.update_layout(*screen.get_size())
            bad_screen.draw()
        elif current_screen=="FINAL":
            final_screen.update_layout(*screen.get_size())
            final_screen.draw()

    bag_icon.draw(screen)
    # 如果背包開啟，畫出背包面板
    if show_shelf:
        draw_bag_shelf(screen, width, height)
    item_preview.draw(screen)

    # 最後把畫面更新到顯示器
    pygame.display.flip()

# 結束 pygame
pygame.quit()
sys.exit()
