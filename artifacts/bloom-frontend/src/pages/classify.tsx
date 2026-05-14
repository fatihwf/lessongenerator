import { useState } from "react";
import { useClassifyBloom } from "@workspace/api-client-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Loader2, Brain, CheckCircle } from "lucide-react";
import { useT } from "@/i18n";

const BLOOM_COLORS: Record<string, string> = {
  remembering: "bg-blue-100 text-blue-800 border-blue-200",
  understanding: "bg-teal-100 text-teal-800 border-teal-200",
  applying: "bg-amber-100 text-amber-800 border-amber-200",
  analyzing: "bg-purple-100 text-purple-800 border-purple-200",
  evaluating: "bg-rose-100 text-rose-800 border-rose-200",
  creating: "bg-emerald-100 text-emerald-800 border-emerald-200",
};

const BLOOM_PYRAMID_KEYS = [
  "creating", "evaluating", "analyzing", "applying", "understanding", "remembering",
] as const;

export default function Classify() {
  const { t } = useT();
  const [text, setText] = useState("");
  const classifyBloom = useClassifyBloom();

  const handleClassify = () => {
    if (!text.trim()) return;
    classifyBloom.mutate({ data: { text, context: null } });
  };

  const result = classifyBloom.data;

  return (
    <div className="max-w-2xl mx-auto space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div>
        <h1 className="text-3xl font-serif font-bold tracking-tight text-primary">{t.classify.title}</h1>
        <p className="text-muted-foreground mt-1">{t.classify.subtitle}</p>
      </div>

      <div className="bg-card border border-card-border rounded-xl p-5 space-y-4">
        <Textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder={t.classify.placeholder}
          rows={4}
          className="resize-none"
        />
        <Button onClick={handleClassify} disabled={classifyBloom.isPending || !text.trim()} className="w-full gap-2">
          {classifyBloom.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Brain className="h-4 w-4" />}
          {classifyBloom.isPending ? t.classify.classifying : t.classify.classifyButton}
        </Button>
      </div>

      {result && (
        <div className="space-y-4">
          <div className={`border rounded-xl p-5 ${BLOOM_COLORS[result.primary_bloom_level] || "bg-muted border-muted-border"}`}>
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <CheckCircle className="h-5 w-5" />
                <span className="font-bold text-lg capitalize">{result.primary_bloom_level}</span>
              </div>
              <span className="text-sm font-medium opacity-80">
                {Math.round(result.confidence * 100)}% {t.classify.confidence}
              </span>
            </div>
            <p className="text-sm opacity-90 leading-relaxed">{result.reasoning}</p>
          </div>

          {result.secondary_levels?.length > 0 && (
            <div className="bg-card border border-card-border rounded-xl p-4">
              <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2">{t.classify.secondaryLevels}</p>
              <div className="flex flex-wrap gap-1.5">
                {result.secondary_levels.map((l) => (
                  <span key={l} className={`px-2.5 py-1 rounded-full text-xs font-medium border ${BLOOM_COLORS[l] || ""}`}>{l}</span>
                ))}
              </div>
            </div>
          )}

          {result.keywords_matched?.length > 0 && (
            <div className="bg-card border border-card-border rounded-xl p-4">
              <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2">{t.classify.matchedKeywords}</p>
              <div className="flex flex-wrap gap-1.5">
                {result.keywords_matched.map((kw, i) => (
                  <code key={i} className="px-2 py-0.5 rounded bg-muted text-foreground text-xs font-mono">{kw}</code>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      <div className="bg-card border border-card-border rounded-xl p-5">
        <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-4">{t.classify.pyramidTitle}</p>
        <div className="space-y-1">
          {BLOOM_PYRAMID_KEYS.map((key, i) => (
            <div
              key={key}
              className={`flex items-center gap-3 px-3 py-2 rounded-lg transition-all ${
                result?.primary_bloom_level === key
                  ? (BLOOM_COLORS[key] + " border font-semibold")
                  : "text-muted-foreground hover:bg-muted/40"
              }`}
              style={{ marginLeft: `${i * 12}px` }}
            >
              <span className="text-sm font-medium w-28 flex-shrink-0">{t.common.bloomLevelLabels[key]}</span>
              <span className="text-xs opacity-70">{t.classify.bloomDescriptions[key]}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
