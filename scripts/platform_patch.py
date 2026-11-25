from pathlib import Path

p = Path("src/App.tsx")
s = p.read_text(encoding="utf-8")

# Global interface terminology and brand.
s = s.replace("آزمون‌یار", "فارسی جاج").replace("آزمون", "مسابقه")
s = s.replace("members.length < 4", "members.length < 3")
s = s.replace("از ۴ عضو", "از ۳ عضو")
s = s.replace("یک تیم چهار نفره", "یک تیم سه‌نفره")
s = s.replace("سه عضو دیگر", "دو عضو دیگر")
s = s.replace("حداکثر ۴ عضو", "حداکثر ۳ عضو")

p.write_text(s, encoding="utf-8")
print("Applied Farsi-Judge naming and three-member team labels.")
