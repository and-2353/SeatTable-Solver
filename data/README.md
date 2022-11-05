# データ構造
## students ディレクトリ
### info.csv
処理対象となる全生徒の情報が保存されている。<br>
info.csv の属性
- id(長さ3)
- display_name(表示名)

### conbi_spec.csv
特定の組み合わせと、それによる加点・減点の情報が保存されている。<br>
conbi_spec.csv の属性
- 生徒_1(display_name 形式)
- 生徒_2(display_name 形式)
- 重み(整数値)

### schedules ディレクトリ
各生徒のスケジュール情報が{id}.csv ファイルに保存されている。<br>
{id}.csv の属性
- 日付(YYYY/M/D 形式)
- 曜日(漢字一字)
- 1～8(0か1)

### subjects ディレクトリ
各生徒の授業情報が{id}.csv ファイルに保存されている。<br>
{id}.csv の属性
- subject(漢字一字)
- lecture_num(授業数)
- is_one_on_one(0か1)

## teachers ディレクトリ
### info.csv
処理対象となる全講師の情報が保存されている。<br>
info.csv の属性
- id(長さ5)
- display_name(表示名)

### schedules ディレクトリ
各講師のスケジュール情報が{id}.csv ファイルに保存されている。<br>
{id}.csv の属性
- 日付(YYYY/M/D 形式)
- 曜日(漢字一字)
- 1～8(0か1)

## データ構造
data/<br>
+-- README.md<br>
+-- students<br>
¦   +-- info.csv<br>
¦   +-- schedules -- {id}.csv<br>
¦   +-- subjects -- {id}.csv<br>
+-- teachers<br>
&nbsp; +-- info.csv<br>
&nbsp; +-- schedules -- {id}.csv<br>
