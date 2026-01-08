# ゲーミフィケーションシステム設計書

## 📋 概要

Habit Tracker RPGは、習慣達成をRPGの成長システムに変換するゲーミフィケーション機能を提供します。本ドキュメントでは、経験値、レベル、ステータス、アチーブメント、ジョブシステムの詳細を説明します。

---

## ⚔️ ステータスシステム

### 6種類のステータス

| ステータス | 略称 | 説明 | 関連カテゴリ |
|-----------|------|------|--------------|
| 体力 (Vitality) | VIT | 身体的な健康と持久力 | exercise, sleep, health |
| 知力 (Intelligence) | INT | 知識と学習能力 | reading, study, learning |
| 精神 (Mental) | MND | 精神的な強さと安定 | meditation, journaling, gratitude, mindfulness |
| 器用 (Dexterity) | DEX | 手先の器用さと創造性 | music, art, craft, hobby |
| 魅力 (Charisma) | CHA | 対人スキルと魅力 | communication, social, grooming |
| 筋力 (Strength) | STR | 筋力とパワー | workout, sports, fitness |

### カテゴリとステータスの対応

```python
CATEGORY_STAT_MAPPING = {
    # VIT (体力) - 健康・運動系
    "exercise": "VIT",
    "sleep": "VIT",
    "health": "VIT",
    
    # INT (知力) - 学習・読書系
    "reading": "INT",
    "study": "INT",
    "learning": "INT",
    
    # MND (精神) - 精神・瞑想系
    "meditation": "MND",
    "journaling": "MND",
    "gratitude": "MND",
    "mindfulness": "MND",
    
    # DEX (器用) - 創作・趣味系
    "music": "DEX",
    "art": "DEX",
    "craft": "DEX",
    "hobby": "DEX",
    
    # CHA (魅力) - 対人・社交系
    "communication": "CHA",
    "social": "CHA",
    "grooming": "CHA",
    
    # STR (筋力) - 筋トレ・スポーツ系
    "workout": "STR",
    "sports": "STR",
    "fitness": "STR",
    
    # デフォルト
    "other": "VIT"
}
```

---

## 📈 経験値システム

### 60日カンスト設計

本システムは**60日間で最大レベル（99）に到達**できるようバランス調整されています。

**想定プレイスタイル:**
- 1日3習慣を達成
- Normal難易度
- 連続達成を維持

### 基本経験値の計算

習慣を達成すると、以下の計算式で経験値が付与されます：

```
獲得EXP = 基本EXP × 難易度係数 × ストリークボーナス × ジョブボーナス
```

### 基本経験値

```python
BASE_EXP = 15
```

### 難易度係数

| 難易度 | 係数 | 獲得EXP目安 |
|--------|------|-------------|
| easy | 0.5 | 7-8 EXP |
| normal | 1.0 | 15 EXP |
| hard | 1.5 | 22-23 EXP |
| very_hard | 2.0 | 30 EXP |

```python
DIFFICULTY_MULTIPLIER = {
    "easy": 0.5,
    "normal": 1.0,
    "hard": 1.5,
    "very_hard": 2.0
}
```

### ストリークボーナス

連続達成日数に応じてボーナスが適用されます：

| 連続日数 | ボーナス倍率 | 説明 |
|----------|--------------|------|
| 3日以上 | 1.1倍 | 習慣の芽生え |
| 7日以上 | 1.25倍 | 一週間の習慣化 |
| 14日以上 | 1.5倍 | 習慣の定着 |
| 30日以上 | 2.0倍 | 完全な習慣化 |
| 60日以上 | 2.5倍 | 習慣のマスター |
| 90日以上 | 3.0倍 | 伝説の継続 |

```python
STREAK_BONUS = [
    {"days": 3, "multiplier": 1.1},
    {"days": 7, "multiplier": 1.25},
    {"days": 14, "multiplier": 1.5},
    {"days": 30, "multiplier": 2.0},
    {"days": 60, "multiplier": 2.5},
    {"days": 90, "multiplier": 3.0},
]
```

### 計算例

```
例1: 普通の習慣を7日連続で達成
  15 × 1.0 × 1.25 × 1.0 = 18.75 → 19 EXP（切り上げ）

例2: 難しい習慣を30日連続で達成（見習い戦士装備）
  15 × 1.5 × 2.0 × 1.05 = 47.25 → 48 EXP
```

---

## 📊 レベルシステム

### 60日カンスト設計

レベルシステムは60日間で最大レベル99に到達できるよう設計されています。

- **基本EXP**: 15（レベル2到達に必要）
- **成長率**: 1.02（緩やかな線形成長）
- **最大レベル**: 99
- **カンスト必要EXP**: 約4,427

### 総合レベル

全ステータスの累計経験値に基づいて総合レベルが決まります。

### レベルアップに必要な経験値

```python
BASE_LEVEL_EXP = 15
GROWTH_RATE = 1.02
MAX_LEVEL = 99

def exp_for_level(level: int) -> int:
    """指定レベルに到達するために必要な累計経験値"""
    if level <= 1:
        return 0
    total = 0
    for lv in range(2, level + 1):
        total += int(BASE_LEVEL_EXP * (GROWTH_RATE ** (lv - 2)))
    return total

def exp_to_next_level(current_level: int, current_exp: int) -> int:
    """次のレベルまでに必要な経験値"""
    next_level_exp = exp_for_level(current_level + 1)
    return next_level_exp - current_exp
```

### レベル別必要経験値テーブル

| レベル | 累計必要EXP | そのレベルへの必要EXP |
|--------|-------------|----------------------|
| 1 | 0 | - |
| 5 | 60 | 16 |
| 10 | 142 | 17 |
| 20 | 334 | 21 |
| 30 | 569 | 26 |
| 40 | 855 | 32 |
| 50 | 1,206 | 39 |
| 60 | 1,635 | 48 |
| 70 | 2,160 | 58 |
| 80 | 2,798 | 71 |
| 90 | 3,579 | 87 |
| 99 | 4,427 | - |

### 60日間のレベルアップ進行（シミュレーション）

1日3習慣（Normal難易度）を毎日達成した場合：

| 日数 | ストリーク | 1日の獲得EXP | 累計EXP | 到達レベル |
|------|-----------|-------------|---------|-----------|
| 1日目 | x1.00 | 45 | 45 | Lv.4 |
| 3日目 | x1.10 | 49 | 139 | Lv.9 |
| 7日目 | x1.25 | 56 | 342 | Lv.20 |
| 14日目 | x1.50 | 67 | 745 | Lv.36 |
| 21日目 | x1.50 | 67 | 1,214 | Lv.50 |
| 30日目 | x2.00 | 90 | 1,840 | Lv.64 |
| 45日目 | x2.00 | 90 | 3,190 | Lv.85 |
| 59日目 | x2.00 | 90 | 4,450 | **Lv.99** 🎉 |
| 60日目 | x2.50 | 112 | 4,562 | Lv.99（カンスト） |

### ステータスレベル

各ステータスも個別にレベルを持ちます。計算式は総合レベルと同じです。

```python
def level_from_exp(exp: int) -> int:
    """経験値からレベルを計算"""
    level = 1
    while level < MAX_LEVEL:
        if exp < exp_for_level(level + 1):
            break
        level += 1
    return level
```

---

## 🏆 アチーブメントシステム

### アチーブメントタイプ

| タイプ | 説明 | 例 |
|--------|------|-----|
| first | 初めて系 | 最初の習慣作成、初めての達成 |
| streak | 連続達成系 | 7日連続、30日連続、100日連続 |
| total | 累計系 | 累計100回達成、累計1000回達成 |
| level | レベル系 | レベル10到達、レベル50到達 |
| stat | ステータス系 | VITが10に到達、全ステータス5以上 |
| special | 特殊 | 隠しアチーブメント |

### レアリティ

| レアリティ | 説明 | 経験値報酬目安 |
|-----------|------|---------------|
| common | コモン | 20 EXP |
| uncommon | アンコモン | 50-100 EXP |
| rare | レア | 200-500 EXP |
| epic | エピック | 1,000 EXP |
| legendary | レジェンダリー | 5,000+ EXP |

### デフォルトアチーブメント一覧

```python
DEFAULT_ACHIEVEMENTS = [
    # First系
    {
        "achievement_id": "first_habit",
        "name": "最初の習慣",
        "description": "最初の習慣を作成する",
        "icon": "🎉",
        "type": "first",
        "rarity": "common",
        "condition": {"type": "first_habit"},
        "exp_reward": 20,
        "sort_order": 0
    },
    {
        "achievement_id": "first_completion",
        "name": "最初の一歩",
        "description": "初めて習慣を達成する",
        "icon": "👣",
        "type": "first",
        "rarity": "common",
        "condition": {"type": "first_completion"},
        "exp_reward": 20,
        "sort_order": 1
    },
    
    # Streak系
    {
        "achievement_id": "streak_3",
        "name": "三日坊主突破",
        "description": "3日連続で習慣を達成する",
        "icon": "🔥",
        "type": "streak",
        "rarity": "common",
        "condition": {"type": "streak", "days": 3},
        "exp_reward": 30,
        "sort_order": 10
    },
    {
        "achievement_id": "streak_7",
        "name": "一週間の習慣",
        "description": "7日連続で習慣を達成する",
        "icon": "🔥",
        "type": "streak",
        "rarity": "uncommon",
        "condition": {"type": "streak", "days": 7},
        "exp_reward": 100,
        "sort_order": 11
    },
    {
        "achievement_id": "streak_14",
        "name": "習慣の定着",
        "description": "14日連続で習慣を達成する",
        "icon": "🔥",
        "type": "streak",
        "rarity": "uncommon",
        "condition": {"type": "streak", "days": 14},
        "exp_reward": 200,
        "sort_order": 12
    },
    {
        "achievement_id": "streak_30",
        "name": "月間マスター",
        "description": "30日連続で習慣を達成する",
        "icon": "🔥",
        "type": "streak",
        "rarity": "rare",
        "condition": {"type": "streak", "days": 30},
        "exp_reward": 500,
        "sort_order": 13
    },
    {
        "achievement_id": "streak_100",
        "name": "習慣の達人",
        "description": "100日連続で習慣を達成する",
        "icon": "💎",
        "type": "streak",
        "rarity": "epic",
        "condition": {"type": "streak", "days": 100},
        "exp_reward": 2000,
        "sort_order": 14
    },
    {
        "achievement_id": "streak_365",
        "name": "一年の継続",
        "description": "365日連続で習慣を達成する",
        "icon": "👑",
        "type": "streak",
        "rarity": "legendary",
        "condition": {"type": "streak", "days": 365},
        "exp_reward": 10000,
        "sort_order": 15
    },
    
    # Total系
    {
        "achievement_id": "total_10",
        "name": "10回の達成",
        "description": "累計10回習慣を達成する",
        "icon": "📊",
        "type": "total",
        "rarity": "common",
        "condition": {"type": "total", "count": 10},
        "exp_reward": 50,
        "sort_order": 20
    },
    {
        "achievement_id": "total_100",
        "name": "100回の達成",
        "description": "累計100回習慣を達成する",
        "icon": "📊",
        "type": "total",
        "rarity": "uncommon",
        "condition": {"type": "total", "count": 100},
        "exp_reward": 200,
        "sort_order": 21
    },
    {
        "achievement_id": "total_1000",
        "name": "1000回の達成",
        "description": "累計1000回習慣を達成する",
        "icon": "📊",
        "type": "total",
        "rarity": "rare",
        "condition": {"type": "total", "count": 1000},
        "exp_reward": 1000,
        "sort_order": 22
    },
    
    # Level系
    {
        "achievement_id": "level_10",
        "name": "レベル10",
        "description": "総合レベル10に到達する",
        "icon": "⭐",
        "type": "level",
        "rarity": "uncommon",
        "condition": {"type": "level", "level": 10},
        "exp_reward": 300,
        "sort_order": 30
    },
    {
        "achievement_id": "level_25",
        "name": "レベル25",
        "description": "総合レベル25に到達する",
        "icon": "⭐",
        "type": "level",
        "rarity": "rare",
        "condition": {"type": "level", "level": 25},
        "exp_reward": 1000,
        "sort_order": 31
    },
    {
        "achievement_id": "level_50",
        "name": "レベル50",
        "description": "総合レベル50に到達する",
        "icon": "🌟",
        "type": "level",
        "rarity": "epic",
        "condition": {"type": "level", "level": 50},
        "exp_reward": 5000,
        "sort_order": 32
    },
    
    # Stat系
    {
        "achievement_id": "stat_5",
        "name": "成長の証",
        "description": "いずれかのステータスが5に到達する",
        "icon": "📈",
        "type": "stat",
        "rarity": "common",
        "condition": {"type": "any_stat", "level": 5},
        "exp_reward": 50,
        "sort_order": 40
    },
    {
        "achievement_id": "stat_10",
        "name": "専門家への道",
        "description": "いずれかのステータスが10に到達する",
        "icon": "📈",
        "type": "stat",
        "rarity": "uncommon",
        "condition": {"type": "any_stat", "level": 10},
        "exp_reward": 200,
        "sort_order": 41
    },
    {
        "achievement_id": "all_stat_5",
        "name": "バランス型",
        "description": "全てのステータスが5以上になる",
        "icon": "⚖️",
        "type": "stat",
        "rarity": "rare",
        "condition": {"type": "all_stats", "level": 5},
        "exp_reward": 500,
        "sort_order": 42
    },
]
```

---

## 👔 ジョブシステム

### ジョブティア

| ティア | 説明 | 解除条件目安 |
|--------|------|-------------|
| novice | 初心者 | 初期状態 |
| apprentice | 見習い | ステータス5以上 |
| journeyman | 熟練者 | ステータス10以上 |
| expert | 達人 | ステータス20以上 |
| master | マスター | ステータス30以上 |
| grandmaster | グランドマスター | ステータス50以上 |

### ジョブボーナス

ジョブを装備すると以下のボーナスが適用されます：

1. **ステータスボーナス**: 特定ステータスに固定値を加算
2. **経験値ボーナス**: 獲得経験値に倍率を適用

### デフォルトジョブ一覧

```python
DEFAULT_JOBS = [
    # Novice
    {
        "job_id": "beginner",
        "name": "ビギナー",
        "description": "すべての冒険者の始まり",
        "icon": "🌱",
        "tier": "novice",
        "requirements": {},
        "stat_bonuses": {},
        "exp_bonus": 1.0,
        "sort_order": 0
    },
    
    # Apprentice (VIT系)
    {
        "job_id": "fighter_apprentice",
        "name": "見習い格闘家",
        "description": "体力を鍛える者",
        "icon": "🥊",
        "tier": "apprentice",
        "requirements": {"stats": {"VIT": 5}},
        "stat_bonuses": {"VIT": 1},
        "exp_bonus": 1.05,
        "sort_order": 10
    },
    
    # Apprentice (INT系)
    {
        "job_id": "scholar_apprentice",
        "name": "見習い学者",
        "description": "知識を追い求める者",
        "icon": "📚",
        "tier": "apprentice",
        "requirements": {"stats": {"INT": 5}},
        "stat_bonuses": {"INT": 1},
        "exp_bonus": 1.05,
        "sort_order": 11
    },
    
    # Apprentice (MND系)
    {
        "job_id": "monk_apprentice",
        "name": "見習い僧侶",
        "description": "精神を鍛える者",
        "icon": "🧘",
        "tier": "apprentice",
        "requirements": {"stats": {"MND": 5}},
        "stat_bonuses": {"MND": 1},
        "exp_bonus": 1.05,
        "sort_order": 12
    },
    
    # Apprentice (DEX系)
    {
        "job_id": "artisan_apprentice",
        "name": "見習い職人",
        "description": "手先の器用さを磨く者",
        "icon": "🎨",
        "tier": "apprentice",
        "requirements": {"stats": {"DEX": 5}},
        "stat_bonuses": {"DEX": 1},
        "exp_bonus": 1.05,
        "sort_order": 13
    },
    
    # Apprentice (CHA系)
    {
        "job_id": "diplomat_apprentice",
        "name": "見習い外交官",
        "description": "人との繋がりを大切にする者",
        "icon": "🤝",
        "tier": "apprentice",
        "requirements": {"stats": {"CHA": 5}},
        "stat_bonuses": {"CHA": 1},
        "exp_bonus": 1.05,
        "sort_order": 14
    },
    
    # Apprentice (STR系)
    {
        "job_id": "warrior_apprentice",
        "name": "見習い戦士",
        "description": "筋力を鍛える者",
        "icon": "⚔️",
        "tier": "apprentice",
        "requirements": {"stats": {"STR": 5}},
        "stat_bonuses": {"STR": 1},
        "exp_bonus": 1.05,
        "sort_order": 15
    },
    
    # Journeyman (VIT系)
    {
        "job_id": "fighter",
        "name": "格闘家",
        "description": "肉体を極めし者",
        "icon": "🥋",
        "tier": "journeyman",
        "requirements": {"stats": {"VIT": 15, "STR": 10}},
        "stat_bonuses": {"VIT": 2, "STR": 1},
        "exp_bonus": 1.10,
        "sort_order": 20
    },
    
    # Journeyman (INT系)
    {
        "job_id": "scholar",
        "name": "学者",
        "description": "豊富な知識を持つ者",
        "icon": "🎓",
        "tier": "journeyman",
        "requirements": {"stats": {"INT": 10}},
        "stat_bonuses": {"INT": 2},
        "exp_bonus": 1.10,
        "sort_order": 21
    },
    
    # Journeyman (MND系)
    {
        "job_id": "monk",
        "name": "僧侶",
        "description": "精神を極めた者",
        "icon": "☯️",
        "tier": "journeyman",
        "requirements": {"stats": {"MND": 10}},
        "stat_bonuses": {"MND": 2},
        "exp_bonus": 1.10,
        "sort_order": 22
    },
    
    # Journeyman (DEX系)
    {
        "job_id": "artisan",
        "name": "職人",
        "description": "匠の技を持つ者",
        "icon": "🔨",
        "tier": "journeyman",
        "requirements": {"stats": {"DEX": 10}},
        "stat_bonuses": {"DEX": 2},
        "exp_bonus": 1.10,
        "sort_order": 23
    },
    
    # Journeyman (CHA系)
    {
        "job_id": "diplomat",
        "name": "外交官",
        "description": "人心を掴む者",
        "icon": "👔",
        "tier": "journeyman",
        "requirements": {"stats": {"CHA": 10}},
        "stat_bonuses": {"CHA": 2},
        "exp_bonus": 1.10,
        "sort_order": 24
    },
    
    # Journeyman (STR系)
    {
        "job_id": "warrior",
        "name": "戦士",
        "description": "強靭な肉体を持つ者",
        "icon": "🛡️",
        "tier": "journeyman",
        "requirements": {"stats": {"STR": 10}},
        "stat_bonuses": {"STR": 2},
        "exp_bonus": 1.10,
        "sort_order": 25
    },
    
    # Expert (バランス型)
    {
        "job_id": "jack_of_all_trades",
        "name": "万能の達人",
        "description": "全ての分野で優れた者",
        "icon": "🌟",
        "tier": "expert",
        "requirements": {
            "stats": {
                "VIT": 10,
                "INT": 10,
                "MND": 10,
                "DEX": 10,
                "CHA": 10,
                "STR": 10
            }
        },
        "stat_bonuses": {
            "VIT": 1,
            "INT": 1,
            "MND": 1,
            "DEX": 1,
            "CHA": 1,
            "STR": 1
        },
        "exp_bonus": 1.20,
        "sort_order": 30
    },
    
    # Expert (VIT系)
    {
        "job_id": "martial_artist",
        "name": "武闘家",
        "description": "肉体の極致に達した格闘の達人",
        "icon": "🥷",
        "tier": "expert",
        "requirements": {
            "stats": {"VIT": 30, "STR": 25},
            "achievements": ["streak_30"]
        },
        "stat_bonuses": {"VIT": 3, "STR": 2},
        "exp_bonus": 1.20,
        "sort_order": 31
    },
    
    # Master (特殊)
    {
        "job_id": "grandmaster_of_habits",
        "name": "習慣の達人",
        "description": "習慣化を極めた伝説の者",
        "icon": "👑",
        "tier": "master",
        "requirements": {
            "stats": {
                "VIT": 25,
                "INT": 25,
                "MND": 25,
                "DEX": 25,
                "CHA": 25,
                "STR": 25
            },
            "level": 50
        },
        "stat_bonuses": {
            "VIT": 3,
            "INT": 3,
            "MND": 3,
            "DEX": 3,
            "CHA": 3,
            "STR": 3
        },
        "exp_bonus": 1.50,
        "sort_order": 100
    },
]
```

---

## 📐 データモデル

### ユーザーステータス構造

```python
@dataclass
class UserStats:
    # 各ステータスのレベル
    vitality: int = 1
    intelligence: int = 1
    mental: int = 1
    dexterity: int = 1
    charisma: int = 1
    strength: int = 1
    
    # 各ステータスの累計経験値
    vitality_exp: int = 0
    intelligence_exp: int = 0
    mental_exp: int = 0
    dexterity_exp: int = 0
    charisma_exp: int = 0
    strength_exp: int = 0
```

### アチーブメント進捗構造

```python
@dataclass
class AchievementProgress:
    achievement_id: str
    achievement: Achievement
    is_unlocked: bool
    unlocked_at: Optional[datetime]
    current_value: int
    target_value: int
    progress_percent: float
```

### ジョブ進捗構造

```python
@dataclass
class JobProgress:
    job_id: str
    job: Job
    is_unlocked: bool
    is_equipped: bool
    unlocked_at: Optional[datetime]
    requirements_met: Dict[str, bool]
    progress_details: Dict[str, Any]
```

---

## 🔄 処理フロー

### 習慣達成時の処理フロー

```
1. 習慣記録を作成
2. ストリークを更新
3. 経験値を計算
   - 基本EXP × 難易度 × ストリークボーナス × ジョブボーナス
4. ユーザーに経験値を付与
   - 総合経験値を加算
   - 対応ステータスの経験値を加算
5. レベルアップ判定
   - 総合レベルの判定
   - ステータスレベルの判定
6. アチーブメント判定
   - ストリーク系
   - 累計達成系
   - レベル系
   - ステータス系
7. ジョブ解除判定
   - ステータス要件のチェック
   - レベル要件のチェック
8. レスポンスを返す
   - 記録情報
   - 獲得経験値
   - レベルアップ情報
   - 解除されたアチーブメント
   - 解除されたジョブ
```

---

## 🎮 ゲームバランス考察

### 成長曲線

- **序盤（レベル1-10）**: 早い成長を実感できる
- **中盤（レベル11-30）**: 安定した成長
- **終盤（レベル31+）**: 長期的な目標として機能

### 難易度設定の指針

| 難易度 | 習慣の例 |
|--------|----------|
| easy | 水を飲む、歯を磨く |
| normal | 30分の読書、ストレッチ |
| hard | 1時間の運動、語学学習 |
| very_hard | フルマラソン練習、資格勉強 |

### モチベーション設計

1. **短期的報酬**: 毎日の経験値獲得
2. **中期的報酬**: ストリークボーナス、アチーブメント
3. **長期的報酬**: レベルアップ、ジョブ解除

---

## 📚 参考資料

- [ゲーミフィケーション入門](https://example.com/gamification)
- [習慣化の科学](https://example.com/habits)
- [RPGレベルデザイン](https://example.com/rpg-design)
