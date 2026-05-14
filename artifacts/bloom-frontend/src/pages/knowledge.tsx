import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import {
  useListChunks,
  getListChunksQueryKey,
  useCreateChunk,
  useRetrieveChunks,
} from "@workspace/api-client-react";
import { useQueryClient } from "@tanstack/react-query";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useToast } from "@/hooks/use-toast";
import { Loader2, Plus, Search, Database } from "lucide-react";
import { useT } from "@/i18n";

const SOURCE_TYPES_TR = ["MEB Ders Kitabı","Öğretmen Notu","Soru Bankası","Etkinlik Föyü","Diğer"];
const SOURCE_TYPES_EN = ["MEB Textbook","Teacher Notes","Question Bank","Activity Sheet","Other"];

const chunkSchema = z.object({
  content: z.string().min(10),
  source_type: z.string().min(1),
  subject: z.string().min(1),
  grade: z.string().optional(),
  unit: z.string().optional(),
  bloom_levels: z.string().optional(),
  source_name: z.string().optional(),
});
type ChunkForm = z.infer<typeof chunkSchema>;

export default function Knowledge() {
  const { toast } = useToast();
  const { t, lang } = useT();
  const queryClient = useQueryClient();
  const [showAdd, setShowAdd] = useState(false);
  const [retrieveQuery, setRetrieveQuery] = useState("");
  const [retrieveResults, setRetrieveResults] = useState<Array<{ chunk_id: number; content: string; score: number; source_type: string }>>([]);

  const SOURCE_TYPES = lang === "tr" ? SOURCE_TYPES_TR : SOURCE_TYPES_EN;

  const { data: chunks = [], isLoading } = useListChunks();
  const createChunk = useCreateChunk();
  const retrieveChunks = useRetrieveChunks();

  const form = useForm<ChunkForm>({
    resolver: zodResolver(chunkSchema),
    defaultValues: { content: "", source_type: "", subject: "" },
  });

  const onSubmit = (values: ChunkForm) => {
    createChunk.mutate(
      {
        data: {
          content: values.content,
          source_type: values.source_type,
          subject: values.subject,
          grade: values.grade || null,
          unit: values.unit || null,
          bloom_levels: values.bloom_levels ? values.bloom_levels.split(",").map(s => s.trim()) : [],
          source_name: values.source_name || null,
        },
      },
      {
        onSuccess: () => {
          queryClient.invalidateQueries({ queryKey: getListChunksQueryKey() });
          toast({ title: t.knowledge.successTitle });
          form.reset();
          setShowAdd(false);
        },
        onError: () => toast({ title: t.knowledge.errorTitle, variant: "destructive" }),
      }
    );
  };

  const handleRetrieve = () => {
    if (!retrieveQuery.trim()) return;
    retrieveChunks.mutate(
      { data: { query: retrieveQuery, top_k: 5 } },
      { onSuccess: (results) => setRetrieveResults(results) }
    );
  };

  return (
    <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-serif font-bold tracking-tight text-primary">{t.knowledge.title}</h1>
          <p className="text-muted-foreground mt-1 text-sm">{t.knowledge.subtitle(chunks.length)}</p>
        </div>
        <Button onClick={() => setShowAdd(!showAdd)} variant="outline" className="gap-2">
          <Plus className="h-4 w-4" /> {t.knowledge.addChunk}
        </Button>
      </div>

      <div className="bg-card border border-card-border rounded-xl p-4">
        <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-3 flex items-center gap-1.5">
          <Search className="h-3.5 w-3.5" /> {t.knowledge.testRetrieval}
        </p>
        <div className="flex gap-2">
          <Input value={retrieveQuery} onChange={(e) => setRetrieveQuery(e.target.value)}
            placeholder={t.knowledge.retrievalPlaceholder} className="flex-1" />
          <Button onClick={handleRetrieve} disabled={retrieveChunks.isPending}>
            {retrieveChunks.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : t.knowledge.retrieveButton}
          </Button>
        </div>
        {retrieveResults.length > 0 && (
          <div className="mt-3 space-y-2">
            {retrieveResults.map((r, i) => (
              <div key={i} className="border border-muted-border rounded-lg p-3 text-xs">
                <div className="flex justify-between mb-1">
                  <span className="font-medium text-foreground">{r.source_type}</span>
                  <span className="text-muted-foreground">{t.knowledge.score}: {r.score.toFixed(3)}</span>
                </div>
                <p className="text-muted-foreground line-clamp-3">{r.content}</p>
              </div>
            ))}
          </div>
        )}
      </div>

      {showAdd && (
        <div className="bg-card border border-card-border rounded-xl p-5">
          <h2 className="font-semibold text-foreground mb-4">{t.knowledge.addChunkTitle}</h2>
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
              <FormField control={form.control} name="content" render={({ field }) => (
                <FormItem>
                  <FormLabel>{t.knowledge.content}</FormLabel>
                  <FormControl><Textarea rows={4} placeholder={t.knowledge.contentPlaceholder} {...field} /></FormControl>
                  <FormMessage />
                </FormItem>
              )} />
              <div className="grid grid-cols-2 gap-4">
                <FormField control={form.control} name="source_type" render={({ field }) => (
                  <FormItem>
                    <FormLabel>{t.knowledge.sourceType}</FormLabel>
                    <Select onValueChange={field.onChange} value={field.value}>
                      <FormControl><SelectTrigger><SelectValue placeholder={t.knowledge.selectSourceType} /></SelectTrigger></FormControl>
                      <SelectContent>{SOURCE_TYPES.map(s => <SelectItem key={s} value={s}>{s}</SelectItem>)}</SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )} />
                <FormField control={form.control} name="subject" render={({ field }) => (
                  <FormItem>
                    <FormLabel>{t.knowledge.subject}</FormLabel>
                    <FormControl><Input placeholder={t.knowledge.subjectPlaceholder} {...field} /></FormControl>
                    <FormMessage />
                  </FormItem>
                )} />
                <FormField control={form.control} name="grade" render={({ field }) => (
                  <FormItem>
                    <FormLabel>{t.knowledge.grade}</FormLabel>
                    <FormControl><Input placeholder={t.knowledge.gradePlaceholder} {...field} /></FormControl>
                    <FormMessage />
                  </FormItem>
                )} />
                <FormField control={form.control} name="unit" render={({ field }) => (
                  <FormItem>
                    <FormLabel>{t.knowledge.unit}</FormLabel>
                    <FormControl><Input placeholder={t.knowledge.unitPlaceholder} {...field} /></FormControl>
                    <FormMessage />
                  </FormItem>
                )} />
              </div>
              <FormField control={form.control} name="bloom_levels" render={({ field }) => (
                <FormItem>
                  <FormLabel>{t.knowledge.bloomLevels}</FormLabel>
                  <FormControl><Input placeholder={t.knowledge.bloomLevelsPlaceholder} {...field} /></FormControl>
                  <FormMessage />
                </FormItem>
              )} />
              <FormField control={form.control} name="source_name" render={({ field }) => (
                <FormItem>
                  <FormLabel>{t.knowledge.sourceName}</FormLabel>
                  <FormControl><Input placeholder={t.knowledge.sourceNamePlaceholder} {...field} /></FormControl>
                  <FormMessage />
                </FormItem>
              )} />
              <div className="flex gap-2">
                <Button type="submit" disabled={createChunk.isPending}>
                  {createChunk.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : t.knowledge.addButton}
                </Button>
                <Button type="button" variant="outline" onClick={() => { setShowAdd(false); form.reset(); }}>
                  {t.knowledge.cancelButton}
                </Button>
              </div>
            </form>
          </Form>
        </div>
      )}

      {isLoading ? (
        <div className="flex items-center justify-center py-16"><Loader2 className="h-6 w-6 animate-spin text-muted-foreground" /></div>
      ) : chunks.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-20 text-center">
          <Database className="h-10 w-10 text-muted-foreground/40 mb-4" />
          <p className="text-foreground font-medium">{t.knowledge.noChunksTitle}</p>
          <p className="text-muted-foreground text-sm mt-1">{t.knowledge.noChunksDesc}</p>
        </div>
      ) : (
        <div className="grid gap-3">
          {chunks.map((c) => (
            <div key={c.id} className="bg-card border border-card-border rounded-xl p-4">
              <div className="flex items-start justify-between gap-3 mb-2">
                <div className="flex items-center gap-2 flex-wrap">
                  <span className="text-xs font-medium text-primary bg-primary/10 px-2 py-0.5 rounded">{c.source_type}</span>
                  <span className="text-xs text-muted-foreground">
                    {c.subject}{c.grade ? ` · ${t.common.grade} ${c.grade}` : ""}{c.unit ? ` · ${c.unit}` : ""}
                  </span>
                </div>
                <div className="flex flex-wrap gap-1">
                  {(c.bloom_levels || []).map((b) => (
                    <span key={b} className="text-xs px-1.5 py-0.5 rounded bg-muted text-muted-foreground">{b}</span>
                  ))}
                </div>
              </div>
              <p className="text-sm text-foreground line-clamp-3">{c.content}</p>
              {c.source_name && <p className="text-xs text-muted-foreground mt-2 italic">{c.source_name}</p>}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
