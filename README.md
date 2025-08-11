1、自动排列会排列所有当前打开的窗口（选中也没有用，但不选中会提示先选中）
2、同步暂时实现不了

Chrome 多用户批量管理工具 安装与使用说明
一、环境准备
操作系统要求
仅支持 macOS 系统（建议 macOS 10.15 及以上）
Python 环境
推荐 Python 3.8 及以上
建议使用虚拟环境（如 venv）
依赖安装
bash
pip install -r requirements.txt
主要依赖：PyQt5, psutil
二、安装步骤
克隆或下载项目源码
bash
git clone <你的仓库地址>
cd Duokai
（可选）创建虚拟环境并激活
bash
python3 -m venv myenv
source myenv/bin/activate
安装依赖包
bash
pip install -r requirements.txt
三、使用方法
启动程序
bash
python3 main.py
主要功能说明
批量检测 Chrome 用户配置文件（Profile）状态
自动扫描 ~/Library/Application Support/Google/Chrome/ 下所有用户目录，准确判断哪些 Profile 已打开。
批量启动选中用户
勾选需要启动的用户，点击“一键批量打开”即可批量启动。
自动排列窗口
点击“自动排列窗口”按钮，所有已打开的 Chrome 窗口会均匀排列并自动置顶显示，方便批量管理和观察。
用户名编辑与保存
可直接在表格中修改用户名，点击“保存”按钮即可保存更名。
注意事项
macOS 限制说明
由于 Chrome 多 Profile 窗口共用同一主进程，无法精确指定某个窗口属于哪个 Profile，自动排列功能会对所有已打开的 Chrome 窗口生效。
窗口排列建议
建议只打开需要排列的 Profile 窗口，关闭其它无关窗口后再点击自动排列。
权限说明
首次运行如遇到“辅助功能权限”提示，请在“系统偏好设置-安全性与隐私-辅助功能”中勾选终端或 Python 解释器。
四、常见问题
窗口无法置顶/排列无效？
请确保已授予辅助功能权限，并关闭无关 Chrome 窗口后重试。
Profile 状态检测不准确？
工具采用检测进程已打开文件的方式，理论上已非常准确。如遇特殊情况，请反馈具体 Profile 目录和现象。
