#!/bin/bash
# 🚀 一键部署脚本到 GitHub + Streamlit Cloud
# 使用方法: ./deploy.sh

set -e

# 配置项 (请根据实际情况修改)
GITHUB_USERNAME="yupeng"  # 替换为你的 GitHub 用户名
REPO_NAME="ai-complaint-handler"
REMOTE_URL="https://github.com/${GITHUB_USERNAME}/${REPO_NAME}.git"

echo "🚀 开始部署 AI 投诉处理助手 v3.0..."

# 1. 检查 Git 配置
if ! git config user.name > /dev/null 2>&1; then
    echo "⚠️  未配置 Git 用户信息，正在配置..."
    git config user.name "yupeng"
    git config user.email "wtueeq@example.com"
fi

# 2. 设置远程仓库
echo "📡 设置远程仓库..."
git remote set-url origin $REMOTE_URL 2>/dev/null || git remote add origin $REMOTE_URL

# 3. 推送代码
echo "📤 推送代码到 GitHub..."
git branch -M main 2>/dev/null || true
git push -u origin main

echo ""
echo "✅ 代码推送成功！"
echo ""
echo "📝 下一步操作:"
echo "1. 访问 https://github.com/${GITHUB_USERNAME}/${REPO_NAME} 确认代码已上传"
echo "2. 访问 https://share.streamlit.io 部署到 Streamlit Cloud"
echo "   - Repository: ${REPO_NAME}"
echo "   - Branch: main"
echo "   - Main file: ai_complaint_handler_v3.py"
echo ""
echo "🎉 部署完成后，你将获得一个公开 URL!"
