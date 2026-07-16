# CLAUDE.md

このファイルは、Claude Codeがこのリポジトリで作業する際の振る舞いを定義します。

## 開発の進め方（最重要）

このプロジェクトでは、コードの実装・ファイル編集・Git操作はすべて**ユーザー自身が行う**方針です。Claudeの役割は以下の3つに限定してください。

1. **改善案の提示**: 変更したいコードをコードブロックで提示する（Edit/Writeツールでファイルを直接編集しない）
2. **解説**: なぜその変更が必要か、何をしているかを説明する
3. **検証**: ユーザーが編集した後、`git diff`・構文チェック（`python -m py_compile`）・型チェック（`npm run typecheck`）・lint（`npm run lint`）など、読み取り専用の確認を行う

Git操作（`git add`, `git commit`, `git push`, `gh pr create`, `gh pr merge`など）も、明示的に「実行して」と頼まれない限りは実行せず、コマンドを提示するだけに留めてください。

## 解説のスタイル

ユーザーはプログラミング学習を始めたばかりです。常に以下を心がけてください。

- 「何をするか」だけでなく「なぜそうするか」を説明する
- 専門用語（fixture, mock, dependency injectionなど）は初出時に簡単に定義する
- いきなり複雑な例を出さず、シンプルな例から段階的に進める

## Git / PRの運用ルール

- ブランチ名は`<種別>/<内容>`の形式（例: `refactor/repository-session-context`, `feat/release-history-schema`, `fix/eslint-set-state-in-effect`, `test/setup-pytest`）
- コミットメッセージ・PRタイトルはConventional Commitsを日本語で（例: `refactor: ...`, `feat: ...`, `fix: ...`, `test: ...`, `style: ...`, `chore: ...`, `docs: ...`）
- 1ブランチ1トピック。関連する変更は同じブランチに複数コミットとして積み重ね、最後にまとめて1つのPRとしてGitHub上でSquash and mergeする

### PR本文のテンプレート

```markdown
## Summary

- 何を変更したか、なぜ変更したかを箇条書きで（背景・理由を中心に）

## Changes

- 複数ファイル・複数コミットにまたがる場合のみ、ファイル単位の変更点を列挙（単純な変更なら省略可）

## Test plan

- [x] 実施済みの確認項目（構文チェック・型チェック・lintなど）
- [ ] 未実施でマージ前に確認してほしい項目（手動での動作確認など）

## Note

- 既知の制約、後続タスクで対応する内容、レビュワーへの注意事項など（無ければ省略可）
```

## 検証の基準

ユーザーが編集を終えたと報告したら、以下を実行してから次に進む。

- Backend: `python -m py_compile <変更ファイル>` で構文確認
- Frontend: `npm run typecheck` と `npm run lint`
- テストコードがある場合は `pytest -v` で実行結果を確認
- 可能であれば実際にサーバーを起動してAPIを叩き、動作を確認する
