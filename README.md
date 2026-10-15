# generate-spec-from-source

ソースコードから仕様書を自動作成する [Kimi Work](https://www.kimi.com/) スキルです。

ソースコード(ファイル / ディレクトリ / Git リポジトリ)を解析し、エビデンスに基づく仕様書(Markdown / Word / PDF)を生成します。

## 特徴

- **インベントリ自動取得**: `scripts/inventory_source.py` が対象の言語別ファイル一覧・行数・Python のクラス/関数/docstring を機械的に抽出
- **証拠ゲート**: ソースに書かれていないことは仕様書に書かない(推測は「推測」「未確認」と明記)
- **テンプレート駆動**: `references/spec-template.md` を雛形に、対象に合わせて章を調整

## 構成

```
generate-spec-from-source/
├── SKILL.md                      # スキル定義(ワークフロー)
├── scripts/
│   └── inventory_source.py       # ソース構造インベントリ
└── references/
    └── spec-template.md          # 仕様書テンプレート
```

## 使い方

### Kimi Work で

リポジトリをスキルとしてインストールするか、`SKILL.md` のワークフローに従ってください。Kimi に対して「このソースから仕様書を作って」と依頼するだけでスキルが適用されます。

### インベントリスクリプト単体

```bash
python scripts/inventory_source.py <対象パス>            # 要約を stdout へ
python scripts/inventory_source.py <対象パス> --json inventory.json
```

## ワークフロー概要

1. **インベントリ取得** — 構造を機械的に取得
2. **ソース精読** — エントリポイントから逆にたどる
3. **仕様抽出** — 構成・処理フロー・データ構造・インターフェース・設定・依存関係
4. **証拠ゲート** — 記述はすべてソースと照合
5. **文書生成** — テンプレートに沿って仕様書を組み立て
6. **納品** — Markdown 既定、docx / pdf は変換スキル併用

## ライセンス

MIT
