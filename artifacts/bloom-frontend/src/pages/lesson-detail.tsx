import { Link, useParams } from "wouter";
import {
  useGetLesson,
  getGetLessonQueryKey,
  useGetLessonTrace,
  getGetLessonTraceQueryKey,
  useSubmitFeedback,
  getListFeedbackQueryKey,
} from "@workspace/api-client-react";
import { useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { useToast } from "@/hooks/use-toast";
import { Loader2, ArrowLeft, Database, Star, ChevronDown, ChevronRight } from "lucide-react";
import { useT } from "@/i18n";

const BLOOM_COLORS: Record<string, string> = {
  remembering: "bg-blue-100 text-blue-800",
  understanding: "bg-teal-100 text-teal-800",
  applying: "bg-amber-100 text-amber-800",
  analyzing: "bg-purple-100 text-purple-800",
  evaluating: "bg-rose-100 text-rose-800",
  creating: "bg-emerald-100 text-emerald-800",
};

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  const [open, setOpen] = useState(true);
  return (
    <div className="border border-card-border rounded-xl overflow-hidden">
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-center justify-between px-5 py-4 bg-card hover:bg-accent/30 transition-colors text-left"
      >
        <span className="font-semibold text-foreground text-sm uppercase tracking-wider">{title}</span>
        {open ? <ChevronDown className="h-4 w-4 text-muted-foreground" /> : <ChevronRight className="h-4 w-4 text-muted-foreground" />}
      </button>
      {open && <div className="px-5 py-4 bg-card text-foreground text-sm leading-relaxed">{children}</div>}
    </div>
  );
}

function RatingButton({ value, current, onClick }: { value: number; current: number; onClick: () => void }) {
  return (
    <button onClick={onClick} className={`p-1 rounded transition-colors ${current >= value ? "text-amber-400" : "text-muted-foreground/30 hover:text-amber-300"}`}>
      <Star className="h-5 w-5 fill-current" />
    </button>
  );
}

export default function LessonDetail() {
  const params = useParams<{ id: string }>();
  const id = parseInt(params.id);
  const { toast } = useToast();
  const { t } = useT();
  const queryClient = useQueryClient();
  const [rating, setRating] = useState(0);
  const [showTrace, setShowTrace] = useState(false);

  const { data: lesson, isLoading } = useGetLesson(id, {
    query: { enabled: !!id, queryKey: getGetLessonQueryKey(id) },
  });
  const { data: trace = [] } = useGetLessonTrace(id, {
    query: { enabled: showTrace && !!id, queryKey: getGetLessonTraceQueryKey(id) },
  });
  const submitFeedback = useSubmitFeedback();

  const handleFeedback = () => {
    if (!rating) { toast({ title: "Önce bir puan seçin" }); return; }
    submitFeedback.mutate(
      { data: { lesson_id: id, rating } },
      {
        onSuccess: () => {
          queryClient.invalidateQueries({ queryKey: getListFeedbackQueryKey() });
          toast({ title: "Geri bildirim gönderildi", description: "Teşekkürler!" });
          setRating(0);
        },
      }
    );
  };

  if (isLoading) return (
    <div className="flex items-center justify-center py-24">
      <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
    </div>
  );

  if (!lesson) return (
    <div className="text-center py-24">
      <p className="text-foreground font-medium">{t.lessonDetail.notFound}</p>
      <Link href="/lessons"><a className="text-primary text-sm mt-2 inline-block">{t.lessonDetail.backToLessons}</a></Link>
    </div>
  );

  const sections = lesson.sections as Record<string, string | string[]>;

  return (
    <div className="max-w-3xl mx-auto space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="flex items-center gap-3">
        <Link href="/lessons">
          <a className="p-2 rounded-lg hover:bg-accent/40 transition-colors">
            <ArrowLeft className="h-4 w-4 text-muted-foreground" />
          </a>
        </Link>
        <div className="flex-1 min-w-0">
          <h1 className="text-xl font-bold text-foreground truncate">{lesson.lesson_title}</h1>
          <p className="text-muted-foreground text-sm">{lesson.subject} · {lesson.unit} · {t.common.grade} {lesson.grade}</p>
        </div>
        <div className="flex items-center gap-2 flex-shrink-0">
          <span className={`px-2.5 py-1 rounded-full text-xs font-medium ${BLOOM_COLORS[lesson.bloom_level] || "bg-muted text-muted-foreground"}`}>
            {lesson.bloom_level}
          </span>
          {lesson.cache_status === "hit" && (
            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-emerald-100 text-emerald-800 border border-emerald-200">
              <Database className="h-3 w-3" /> {t.lessonDetail.cached}
            </span>
          )}
          {lesson.generation_info && (
            <div className="flex flex-col gap-1">
              <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium ${lesson.generation_info.source === "LLM" ? "bg-blue-100 text-blue-800 border-blue-200" : "bg-orange-100 text-orange-800 border-orange-200"} border`}>
                {lesson.generation_info.source === "LLM" ? "DeepSeek" : "Fallback"} ({lesson.generation_info.model})
              </span>
              {lesson.generation_info.source === "FALLBACK" && lesson.generation_info.error_detail && (
                <span className="text-[10px] text-rose-500 font-mono max-w-xs truncate" title={lesson.generation_info.error_detail}>
                  Error: {lesson.generation_info.error_detail}
                </span>
              )}
            </div>
          )}
        </div>
      </div>

      {lesson.bloom_map?.length > 0 && (
        <div className="bg-card border border-card-border rounded-xl p-4">
          <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2">{t.lessonDetail.bloomMap}</p>
          <div className="flex flex-wrap gap-1.5">
            {lesson.bloom_map.map((v, i) => (
              <span key={i} className="px-2 py-0.5 rounded bg-primary/10 text-primary text-xs font-medium">{v}</span>
            ))}
          </div>
        </div>
      )}

      {lesson.personalization_summary && Object.keys(lesson.personalization_summary).length > 0 && (
        <div className="bg-primary/5 border border-primary/20 rounded-xl p-4 text-sm">
          <p className="text-xs font-semibold text-primary uppercase tracking-wider mb-2">{t.lessonDetail.personalization}</p>
          {Object.entries(lesson.personalization_summary as Record<string, string>).map(([k, v]) => (
            <p key={k} className="text-muted-foreground">
              <span className="text-foreground font-medium capitalize">{k.replace(/_/g, " ")}:</span> {v}
            </p>
          ))}
        </div>
      )}

      <div className="space-y-3">
        {sections.introduction && (
          <Section title={t.lessonDetail.introduction}><p>{String(sections.introduction)}</p></Section>
        )}
        {sections.explanation && (
          <Section title={t.lessonDetail.explanation}><p>{String(sections.explanation)}</p></Section>
        )}
        {Array.isArray(sections.examples) && sections.examples.length > 0 && (
          <Section title={t.lessonDetail.examples}>
            <ul className="space-y-2">
              {(sections.examples as string[]).map((ex, i) => (
                <li key={i} className="flex gap-2">
                  <span className="text-primary font-bold flex-shrink-0">{i + 1}.</span>
                  <span>{ex}</span>
                </li>
              ))}
            </ul>
          </Section>
        )}
        {Array.isArray(sections.practice) && sections.practice.length > 0 && (
          <Section title={t.lessonDetail.practice}>
            <ul className="space-y-2">
              {(sections.practice as string[]).map((p, i) => (
                <li key={i} className="flex gap-2">
                  <span className="text-amber-600 font-bold flex-shrink-0">{i + 1}.</span>
                  <span>{p}</span>
                </li>
              ))}
            </ul>
          </Section>
        )}
        {Array.isArray(sections.misconceptions) && sections.misconceptions.length > 0 && (
          <Section title={t.lessonDetail.misconceptions}>
            <ul className="space-y-2">
              {(sections.misconceptions as string[]).map((m, i) => (
                <li key={i} className="flex gap-2">
                  <span className="text-rose-500 font-bold flex-shrink-0">!</span>
                  <span>{m}</span>
                </li>
              ))}
            </ul>
          </Section>
        )}
        {sections.summary && (
          <Section title={t.lessonDetail.summary}><p>{String(sections.summary)}</p></Section>
        )}
        {Array.isArray(sections.assessment) && sections.assessment.length > 0 && (
          <Section title={t.lessonDetail.assessment}>
            <ul className="space-y-2">
              {(sections.assessment as string[]).map((q, i) => (
                <li key={i} className="flex gap-2">
                  <span className="text-purple-600 font-bold flex-shrink-0">S{i + 1}.</span>
                  <span>{q}</span>
                </li>
              ))}
            </ul>
          </Section>
        )}
      </div>

      {lesson.sources_used?.length > 0 && (
        <div className="bg-muted/30 border border-muted-border rounded-xl p-4 text-sm">
          <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2">{t.lessonDetail.sourcesUsed}</p>
          <ul className="space-y-1">
            {lesson.sources_used.map((s, i) => (
              <li key={i} className="text-muted-foreground">{s}</li>
            ))}
          </ul>
        </div>
      )}

      <div className="bg-card border border-card-border rounded-xl p-4">
        <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-3">{t.lessonDetail.rateLesson}</p>
        <div className="flex items-center gap-2">
          {[1, 2, 3, 4, 5].map((v) => (
            <RatingButton key={v} value={v} current={rating} onClick={() => setRating(v)} />
          ))}
          <Button size="sm" onClick={handleFeedback} disabled={submitFeedback.isPending || !rating} className="ml-3">
            {submitFeedback.isPending ? <Loader2 className="h-3 w-3 animate-spin" /> : t.lessonDetail.submitFeedback}
          </Button>
        </div>
      </div>

      <div>
        <button
          onClick={() => setShowTrace(!showTrace)}
          className="text-xs text-muted-foreground hover:text-foreground transition-colors flex items-center gap-1"
        >
          {showTrace ? <ChevronDown className="h-3 w-3" /> : <ChevronRight className="h-3 w-3" />}
          {t.lessonDetail.retrievalTrace(trace.length)}
        </button>
        {showTrace && trace.length > 0 && (
          <div className="mt-2 space-y-2">
            {trace.map((tr, i) => (
              <div key={i} className="border border-muted-border rounded-lg p-3 text-xs">
                <div className="flex items-center justify-between mb-1">
                  <span className="font-medium text-foreground">Parça #{tr.chunk_id} · {tr.source_type}</span>
                  <div className="flex items-center gap-2">
                    <span className="text-muted-foreground">{t.knowledge.score}: {tr.score.toFixed(3)}</span>
                    {tr.bloom_match && <span className="text-emerald-600 font-medium">bloom ✓</span>}
                  </div>
                </div>
                <p className="text-muted-foreground line-clamp-2">{tr.content}</p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
