# Justin’s ArtVerse

一个宇宙主题的插画作品集网站,用 GitHub Pages 免费托管。
你只需要把画好的图放进 `art/` 文件夹,GitHub 会自动压缩图片、生成网站并上线。

---

## 一、第一次部署(只做一次)

1. **新建仓库**:登录 GitHub → 右上角 **+** → **New repository**。
   - 名字随便起,比如 `artverse`,网址会是 `https://你的用户名.github.io/artverse/`。
   - 如果名字叫 `你的用户名.github.io`,网址就是更短的 `https://你的用户名.github.io/`。
   - 选 **Public**(免费账号的 Pages 需要公开仓库)。
2. **上传文件**:把这个文件夹里的所有东西传到仓库。
   - 最省事:用 [GitHub Desktop](https://desktop.github.com/),把文件夹拖进去,Commit,再 Push。
   - 用网页上传:在仓库页面点 **Add file → Upload files**,把文件全部拖进去。
     注意 `.github` 是**隐藏文件夹**,Mac 访达里先按 `Cmd + Shift + .` 显示隐藏文件,再一起拖。
3. **打开 Pages**:仓库 **Settings → Pages**,把 **Source** 选成 **GitHub Actions**。
4. **等它上线**:点仓库顶部的 **Actions**,看到绿色对勾就好了(第一次大约 1–2 分钟)。
   网址显示在 Settings → Pages 页面顶部。

> 如果第 3 步之前 Actions 已经跑过并失败了,设置好 Source 之后,到 Actions 里点 **Build and deploy the ArtVerse → Run workflow** 重新跑一次。

---

## 二、日常上传作品

**每个文件夹 = 一个系列(网站上的一颗星球)。**

```
art/
├── 01 Characters/          ← 系列「Characters」
│   ├── 01 Star Girl.png
│   ├── 02 Moonlit Fox.png
│   └── _info.json          ← 可选:系列介绍、封面、每幅画的标题
├── 02 Space Dreams/        ← 系列「Space Dreams」
│   └── nebula-cat.jpg
└── loose sketch.jpg        ← 直接放在 art/ 里的,算「Uncategorized」
```

- **上传图片**:在 GitHub 打开对应文件夹 → **Add file → Upload files** → 拖进图片 → **Commit changes**。
  几分钟后网站自动更新。iPad 上用 Safari 打开 GitHub 网页也能这样传。
- **新建系列**:在电脑上直接把整个文件夹拖到上传页面就行。
  或者在 `art/` 里点 **Add file → Create new file**,文件名输入 `New Series/_info.json`(打 `/` 会自动变成文件夹),内容写 `{}`,保存后再往里传图。
- **作品标题**来自文件名:`02 Moonlit Fox.png` → 「Moonlit Fox」。`IMG_2041.jpg` 这种会显示「Untitled」。
- **排序**:文件名或文件夹名前面加数字(`01 `、`02-`)就按数字排,网页上不会显示数字。没加数字的,新传的排在前面。
- **支持格式**:JPG、PNG、WebP、HEIC、GIF,以及 mp4 / webm 动画(Procreate 导出的缩时视频或动画)。
  原图多大都行,网站会自动生成适合网页的小图。网页上传单个文件上限 25MB。

### 可选:`_info.json`(放在系列文件夹里)

```json
{
  "description": "People and creatures from my sketchbook",
  "cover": "01 Star Girl.png",
  "order": 1,
  "works": {
    "02 Moonlit Fox.png": {
      "title": "Moonlit Fox",
      "year": "2025",
      "description": "A fox waiting for the moon to rise."
    }
  }
}
```

全部字段都可以不写。`cover` 是这颗星球表面显示的图;`order` 决定系列的先后。

---

## 三、改网站信息:`site.json`

在 GitHub 上点开 `site.json` → 右上角铅笔图标编辑 → **Commit changes**。

| 字段 | 作用 |
|---|---|
| `name` | 网站名字,首页大标题(空格处换行) |
| `tagline` | 首页左下角的一句话,`\n` 是换行 |
| `bio` | About 区的自我介绍 |
| `description` | 搜索引擎和分享链接里显示的简介 |
| `email` | 联系邮箱,留空就不显示 |
| `links` | 社交账号,例如 `{ "label": "Instagram", "url": "instagram.com/你的账号" }`,url 留空不显示 |
| `accent` | 主题光晕色,推荐 `#A78BFA` 紫、`#67E8F9` 青、`#F472B6` 粉、`#FBBF24` 金 |
| `defaultMedium` | 每幅画默认显示的工具,默认 `Procreate` |
| `featured` | 首页公转的作品,例如 `["01 Characters/01 Star Girl.png"]`,留空就用最新的 8 幅 |

---

## 四、出问题了?

- **Actions 出现红叉**:点进去看 `python scripts/build.py` 那一步的日志,`WARNING` 会写明哪个文件有问题(比如 JSON 少了逗号)。
- **网页没变化**:等 Actions 跑完再刷新;浏览器有缓存的话按 `Cmd + Shift + R`。
- **本地预览**:直接双击 `index.html` 能看到带示例画面的效果;想看自己的作品,运行
  `pip install -r requirements.txt && python scripts/build.py`,然后打开 `_site/index.html`。
