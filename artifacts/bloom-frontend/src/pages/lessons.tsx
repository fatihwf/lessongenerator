import { useState } from "react";
import { Link } from "wouter";
import { useListLessons, useListProfiles } from "@workspace/api-client-react";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Loader2, BookOpen, Zap, Database } from "lucide-react";
import { useT } from "@/i18n";

const BLOOM_COLORS: Record<string, string> = {
  remembering: "bg-blue-100 text-blue-800 border-blue-200",
  understanding: "bg-teal-100 text-teal-800 border-teal-200",
  applying: "bg-amber-100 text-amber-800 border-amber-200",
  analyzing: "bg-purple-100 text-purple-800 border-purple-200",
  evaluating: "bg-rose-100 text-rose-800 border-rose-200",
  creating: "bg-emerald-100 text-emerald-800 border-emerald-200",
};

export default function Lessons() {
  const { t } = useT();
  const [filterGrade, setFilterGrade] = useState<string>("");
  const [filterProfile, setFilterProfile] = useState<string>("");

  const { data: profiles = [] } = useListProfiles();
  const { data: lessons = [], isLoading } = useListLessons({
    grade: filterGrade || undefined,
    profile_id: filterProfile ? parseInt(filterProfile) : undefined,
  });

  return (
    <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-serif font-bold tracking-tight text-primary">{t.lessons.title}</h1>
          <p className="text-muted-foreground mt-1 text-sm">{t.lessons.lessonCount(lessons.length)}</p>
        </div>
        <Link href="/generate" className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-primary text-primary-foreground text-sm font-medium hover-elevate transition-colors">
          <Zap className="h-4 w-4" /> {t.lessons.generateNew}
        </Link>
      </div>

      <div className="flex flex-wrap gap-3">
        <Select onValueChange={(v) => setFilterGrade(v === "all" ? "" : v)} value={filterGrade || "all"}>
          <SelectTrigger className="w-40">
            <SelectValue placeholder={t.lessons.filterGrade} />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">{t.lessons.filterGrade}</SelectItem>
            {["5","6","7","8","9","10","11","12"].map(g => (
              <SelectItem key={g} value={g}>{t.lessons.gradeN(g)}</SelectItem>
            ))}
          </SelectContent>
        </Select>

        <Select onValueChange={(v) => setFilterProfile(v === "all" ? "" : v)} value={filterProfile || "all"}>
          <SelectTrigger className="w-48">
            <SelectValue placeholder={t.lessons.filterProfile} />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">{t.lessons.filterProfile}</SelectItem>
            {profiles.map(p => <SelectItem key={p.id} value={String(p.id)}>{p.name}</SelectItem>)}
          </SelectContent>
        </Select>
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center py-16">
          <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
        </div>
      ) : lessons.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-20 text-center">
          <BookOpen className="h-10 w-10 text-muted-foreground/40 mb-4" />
          <p className="text-foreground font-medium">{t.lessons.noLessonsTitle}</p>
          <p className="text-muted-foreground text-sm mt-1">{t.lessons.noLessonsDesc}</p>
          <Link href="/generate" className="mt-4 inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-primary text-primary-foreground text-sm font-medium">
            <Zap className="h-4 w-4" /> {t.lessons.generateFirst}
          </Link>
        </div>
      ) : (
        <div className="grid gap-4">
          {lessons.map((lesson) => (
            <Link key={lesson.id} href={`/lessons/${lesson.id}`} className="block bg-card border border-card-border rounded-xl p-5 hover-elevate transition-all cursor-pointer">
                <div className="flex items-start justify-between gap-4">
                  <div className="min-w-0 flex-1">
                    <h3 className="font-semibold text-foreground truncate">{lesson.lesson_title}</h3>
                    <p className="text-muted-foreground text-sm mt-0.5">
                      {lesson.subject} · {lesson.unit} · {t.common.grade} {lesson.grade}
                    </p>
                  </div>
                  <div className="flex items-center gap-2 flex-shrink-0">
                    <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium border ${BLOOM_COLORS[lesson.bloom_level] || "bg-muted text-muted-foreground border-muted-border"}`}>
                      {lesson.bloom_level}
                    </span>
                    {lesson.cache_status === "hit" && (
                      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-emerald-100 text-emerald-800 border border-emerald-200">
                        <Database className="h-3 w-3" /> {t.lessons.cached}
                      </span>
                    )}
                  </div>
                </div>
                <p className="text-muted-foreground text-xs mt-3">
                  {new Date(lesson.created_at).toLocaleDateString("tr-TR", { dateStyle: "medium" })}
                </p>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
