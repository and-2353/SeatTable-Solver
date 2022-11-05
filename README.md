# SeatTableSolver
個別指導塾における、講習コマ配置のソルバー。遺伝的アルゴリズムを使用

## パラメータ
- 生徒のスケジュール
  - `/data/students/schedules` 内に配置
- 生徒の授業科目
  - `/data/students/subjects` 内に配置
- 特定生徒の相性
  - `/data/students` 内に配置
- 生徒IDと生徒表示名の対応表
  - `/data/students` 内に配置
- 講師のスケジュール
  - `/data/teachers/schedules` 内に配置
- 講師IDと講師表示名の対応表
  - `/data/teachers` 内に配置
- 講師と生徒の担当表
  - `/data/` 内に配置
- 評価関数・評価関数の重み
    - `Classes/UniTable.py` 内`calculate_score()`内に配置されている関数を調整
- 遺伝的アルゴリズム関連の変数
  - `utils.py` 内`decide_constants()` 内に配置されている定数を調整
    - 第1世代目の探索回数：N_SEARCH
    - 1世代でキャンセルする探索回数：N_CANCEL
    - 1世代で再登録する探索回数：N_RESOLVE
    - 次の世代に残されるテーブル数：N_KEEPTABLE
    - 世代数：N_GENERATIONS

## データ構造
### students ディレクトリ
#### info.csv
処理対象となる全生徒の情報が保存されている。<br>
info.csv の属性
- id(長さ3)
- display_name(表示名)

#### conbi_spec.csv
特定の組み合わせと、それによる加点・減点の情報が保存されている。<br>
conbi_spec.csv の属性
- 生徒_1(display_name 形式)
- 生徒_2(display_name 形式)
- 重み(整数値)

#### schedules ディレクトリ
各生徒のスケジュール情報が{id}.csv ファイルに保存されている。<br>
{id}.csv の属性
- 日付(YYYY/M/D 形式)
- 曜日(漢字一字)
- 1～8(0か1)

#### subjects ディレクトリ
各生徒の授業情報が{id}.csv ファイルに保存されている。<br>
{id}.csv の属性
- subject(漢字一字)
- lecture_num(授業数)
- is_one_on_one(0か1)

### teachers ディレクトリ
#### info.csv
処理対象となる全講師の情報が保存されている。<br>
info.csv の属性
- id(長さ5)
- display_name(表示名)

#### schedules ディレクトリ
各講師のスケジュール情報が{id}.csv ファイルに保存されている。<br>
{id}.csv の属性
- 日付(YYYY/M/D 形式)
- 曜日(漢字一字)
- 1～8(0か1)

### データ構造
data/<br>
+-- README.md<br>
+-- students<br>
¦   +-- info.csv<br>
¦   +-- schedules -- {id}.csv<br>
¦   +-- subjects -- {id}.csv<br>
+-- teachers<br>
&nbsp; +-- info.csv<br>
&nbsp; +-- schedules -- {id}.csv<br>
