import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import {
  useListProfiles,
  useListOutcomes,
  useGenerateLesson,
  getListLessonsQueryKey,
  getGetLessonStatsQueryKey,
} from "@workspace/api-client-react";
import { useQueryClient } from "@tanstack/react-query";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";
import { useToast } from "@/hooks/use-toast";
import { Loader2, Sparkles, BookOpen, User } from "lucide-react";
import { useLocation } from "wouter";
import { useT } from "@/i18n";

const BLOOM_LEVEL_KEYS = ["remembering", "understanding", "applying", "analyzing", "evaluating", "creating"] as const;

const schema = z.object({
  outcome_id: z.string().min(1),
  profile_id: z.string().min(1),
  target_bloom_level: z.string().optional(),
  force_regenerate: z.boolean().default(false),
});
type FormData = z.infer<typeof schema>;

export default function Generate() {
  const [, navigate] = useLocation();
  const { toast } = useToast();
  const { t } = useT();
  const queryClient = useQueryClient();
  const { data: profiles = [], isLoading: profilesLoading } = useListProfiles();
  const { data: outcomes = [], isLoading: outcomesLoading } = useListOutcomes();
  const generateLesson = useGenerateLesson();

  const form = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: { force_regenerate: false },
  });

  const onSubmit = (values: FormData) => {
    generateLesson.mutate(
      {
        data: {
          outcome_id: parseInt(values.outcome_id),
          profile_id: parseInt(values.profile_id),
          target_bloom_level: values.target_bloom_level || null,
          force_regenerate: values.force_regenerate,
        },
      },
      {
        onSuccess: (lesson) => {
          queryClient.invalidateQueries({ queryKey: getListLessonsQueryKey() });
          queryClient.invalidateQueries({ queryKey: getGetLessonStatsQueryKey() });
          toast({ title: t.generate.successTitle, description: lesson.lesson_title });
          navigate(`/lessons/${lesson.id}`);
        },
        onError: () => {
          toast({ title: t.generate.errorTitle, description: t.generate.errorDesc, variant: "destructive" });
        },
      }
    );
  };

  const isLoading = profilesLoading || outcomesLoading;

  return (
    <div className="max-w-2xl mx-auto space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div>
        <h1 className="text-3xl font-serif font-bold tracking-tight text-primary">{t.generate.title}</h1>
        <p className="text-muted-foreground mt-1">{t.generate.subtitle}</p>
      </div>

      <div className="bg-card border border-card-border rounded-xl p-6 shadow-sm">
        {isLoading ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
          </div>
        ) : (
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
              <FormField
                control={form.control}
                name="profile_id"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel className="flex items-center gap-2 text-foreground font-medium">
                      <User className="h-4 w-4 text-primary" />
                      {t.generate.learnerProfile}
                    </FormLabel>
                    <Select onValueChange={field.onChange} value={field.value}>
                      <FormControl>
                        <SelectTrigger><SelectValue placeholder={t.generate.selectProfile} /></SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        {profiles.map((p) => (
                          <SelectItem key={p.id} value={String(p.id)}>
                            {p.name} — {t.common.grade} {p.grade} ({p.proficiency_level})
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="outcome_id"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel className="flex items-center gap-2 text-foreground font-medium">
                      <BookOpen className="h-4 w-4 text-primary" />
                      {t.generate.curriculumOutcome}
                    </FormLabel>
                    <Select onValueChange={field.onChange} value={field.value}>
                      <FormControl>
                        <SelectTrigger><SelectValue placeholder={t.generate.selectOutcome} /></SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        {outcomes.map((o) => (
                          <SelectItem key={o.id} value={String(o.id)}>
                            {o.subject} · {o.unit} · {o.bloom_level}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="target_bloom_level"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel className="text-foreground font-medium">
                      {t.generate.overrideBloom}{" "}
                      <span className="text-muted-foreground font-normal">{t.generate.overrideBloomOptional}</span>
                    </FormLabel>
                    <Select onValueChange={field.onChange} value={field.value}>
                      <FormControl>
                        <SelectTrigger><SelectValue placeholder={t.generate.useDetectedLevel} /></SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        {BLOOM_LEVEL_KEYS.map((b) => (
                          <SelectItem key={b} value={b}>
                            {t.common.bloomLevelLabels[b]}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="force_regenerate"
                render={({ field }) => (
                  <FormItem className="flex items-center justify-between rounded-lg border border-border p-4">
                    <div>
                      <FormLabel className="text-foreground font-medium cursor-pointer">
                        {t.generate.forceRegenerate}
                      </FormLabel>
                      <p className="text-muted-foreground text-xs mt-0.5">{t.generate.forceRegenerateDesc}</p>
                    </div>
                    <FormControl>
                      <Switch checked={field.value} onCheckedChange={field.onChange} />
                    </FormControl>
                  </FormItem>
                )}
              />

              <Button type="submit" disabled={generateLesson.isPending} className="w-full gap-2">
                {generateLesson.isPending ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <Sparkles className="h-4 w-4" />
                )}
                {generateLesson.isPending ? t.generate.generating : t.generate.generateButton}
              </Button>
            </form>
          </Form>
        )}
      </div>
    </div>
  );
}
