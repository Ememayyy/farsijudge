from pathlib import Path

path = Path("farsijudge/src/App.tsx")
source = path.read_text(encoding="utf-8")

changes = [
    (
        "  useEffect(() => {\n    if (!selectedExam || page !== 'exam') return\n",
        "  useEffect(() => {\n    const client = supabase\n    if (!selectedExam || page !== 'exam') return\n",
    ),
    (
        "    if (!supabase || !session?.user.id) return\n    let alive = true\n    const load = async () => {\n      if (selectedStatus === 'active') {\n        const { error: startError } = await supabase.rpc('start_exam', { p_exam_id: selectedExam.id })",
        "    if (!client || !session?.user.id) return\n    let alive = true\n    const load = async () => {\n      if (selectedStatus === 'active') {\n        const { error: startError } = await client.rpc('start_exam', { p_exam_id: selectedExam.id })",
    ),
    ("        supabase.from('exam_questions')", "        client.from('exam_questions')"),
    ("        supabase.from('exam_answers')", "        client.from('exam_answers')"),
    (
        "        await supabase.rpc('finalize_exam', { p_exam_id: selectedExam.id })\n        const resultRes = await supabase.from('exam_results')",
        "        await client.rpc('finalize_exam', { p_exam_id: selectedExam.id })\n        const resultRes = await client.from('exam_results')",
    ),
    (
        "  useEffect(() => {\n    if (!selectedExam || page !== 'exam' || getStatus(selectedExam, now) !== 'ended' || isDemo || !supabase || !session?.user.id) return\n",
        "  useEffect(() => {\n    const client = supabase\n    if (!selectedExam || page !== 'exam' || getStatus(selectedExam, now) !== 'ended' || isDemo || !client || !session?.user.id) return\n",
    ),
    (
        "      const { error } = await supabase.rpc('finalize_exam', { p_exam_id: selectedExam.id })",
        "      const { error } = await client.rpc('finalize_exam', { p_exam_id: selectedExam.id })",
    ),
    (
        "      const { data } = await supabase.from('exam_results')",
        "      const { data } = await client.from('exam_results')",
    ),
    (
        "  useEffect(() => {\n    if (!answerDirty || !selectedExam || page !== 'exam' || selectedStatus !== 'active') return\n",
        "  useEffect(() => {\n    const client = supabase\n    if (!answerDirty || !selectedExam || page !== 'exam' || selectedStatus !== 'active') return\n",
    ),
    (
        "      if (!supabase || !session?.user.id) return\n      const operations =",
        "      if (!client || !session?.user.id) return\n      const operations =",
    ),
    ("          return supabase.from('exam_answers')", "          return client.from('exam_answers')"),
    ("        return supabase.from('exam_answers')", "        return client.from('exam_answers')"),
    (
        "  useEffect(() => {\n    if (!isAdmin || !supabase || !session?.user.id || page !== 'admin') return\n",
        "  useEffect(() => {\n    const client = supabase\n    if (!isAdmin || !client || !session?.user.id || page !== 'admin') return\n",
    ),
    ("        supabase.from('exam_results')", "        client.from('exam_results')"),
    ("        supabase.from('profiles')", "        client.from('profiles')"),
]

for old, new in changes:
    count = source.count(old)
    if count != 1:
        raise SystemExit(f"Expected exactly one match, found {count}: {old[:90]!r}")
    source = source.replace(old, new, 1)

path.write_text(source, encoding="utf-8")
print("Applied Supabase client narrowing fix.")
