name: CD

on:
  push:
    branches: [ "main" ]

jobs:
  deploy:
    runs-on: ubuntu-latest

    # 只有在 CI 成功時才跑（可選）
    needs: []
    # 如果你想 CI -> CD 串起來，可把 needs: 改成指向 CI job 名稱
    # 例如 needs: [test]

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install deps for deploy
        run: |
          python -m pip install --upgrade pip
          if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
          if [ -f pyproject.toml ]; then pip install .; fi

      - name: Run deploy script
        env:
          API_KEY: ${{ secrets.API_KEY }}
          DEPLOY_TOKEN: ${{ secrets.DEPLOY_TOKEN }}
        run: |
          python deploy.py
