import { useState } from "react";
import { useListOutcomes, useCreateOutcome } from "@workspace/api-client-react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger,
} from "@/components/ui/dialog";
import { Target, Plus, Book, Lightbulb } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { useT } from "@/i18n";

export default function Curriculum() {
  const { data: outcomes, isLoading, refetch } = useListOutcomes();
  const createOutcome = useCreateOutcome();
  const { toast } = useToast();
  const { t } = useT();

  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [formData, setFormData] = useState({ subject: "", grade: "", unit: "", outcome_text: "" });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    createOutcome.mutate(
      { data: formData },
      {
        onSuccess: () => {
          toast({ title: t.curriculum.successTitle, description: t.curriculum.successDesc });
          setIsDialogOpen(false);
          setFormData({ subject: "", grade: "", unit: "", outcome_text: "" });
          refetch();
        },
        onError: () => {
          toast({ title: t.curriculum.errorTitle, description: t.curriculum.errorDesc, variant: "destructive" });
        }
      }
    );
  };

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <h1 className="text-3xl font-serif font-bold tracking-tight text-primary">{t.curriculum.title}</h1>
          <p className="text-muted-foreground mt-1">{t.curriculum.subtitle}</p>
        </div>

        <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
          <DialogTrigger asChild>
            <Button className="gap-2"><Plus className="h-4 w-4" />{t.curriculum.addOutcome}</Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>{t.curriculum.dialogTitle}</DialogTitle>
              <DialogDescription>{t.curriculum.dialogDesc}</DialogDescription>
            </DialogHeader>
            <form onSubmit={handleSubmit} className="space-y-4 pt-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="subject">{t.curriculum.subject}</Label>
                  <Input id="subject" required value={formData.subject}
                    onChange={e => setFormData({...formData, subject: e.target.value})}
                    placeholder={t.curriculum.subjectPlaceholder} />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="grade">{t.curriculum.grade}</Label>
                  <Input id="grade" required value={formData.grade}
                    onChange={e => setFormData({...formData, grade: e.target.value})}
                    placeholder={t.curriculum.gradePlaceholder} />
                </div>
              </div>
              <div className="space-y-2">
                <Label htmlFor="unit">{t.curriculum.unit}</Label>
                <Input id="unit" required value={formData.unit}
                  onChange={e => setFormData({...formData, unit: e.target.value})}
                  placeholder={t.curriculum.unitPlaceholder} />
              </div>
              <div className="space-y-2">
                <Label htmlFor="outcome">{t.curriculum.outcomeText}</Label>
                <Textarea id="outcome" required value={formData.outcome_text}
                  onChange={e => setFormData({...formData, outcome_text: e.target.value})}
                  placeholder={t.curriculum.outcomeTextPlaceholder} rows={4} />
              </div>
              <Button type="submit" className="w-full" disabled={createOutcome.isPending}>
                {createOutcome.isPending ? t.curriculum.saving : t.curriculum.saveButton}
              </Button>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      {isLoading ? (
        <div className="grid gap-4">
          {[1,2,3].map(i => (
            <div key={i} className="h-32 bg-card rounded-lg border border-border animate-pulse" />
          ))}
        </div>
      ) : outcomes && outcomes.length > 0 ? (
        <div className="grid gap-4">
          {outcomes.map(outcome => (
            <Card key={outcome.id}>
              <CardContent className="p-6">
                <div className="flex flex-col md:flex-row md:items-start gap-4 justify-between">
                  <div className="space-y-2 flex-1">
                    <div className="flex items-center gap-2 text-sm text-muted-foreground font-medium">
                      <Book className="h-4 w-4" />
                      <span>{outcome.subject}</span>
                      <span>•</span>
                      <span>{t.common.grade} {outcome.grade}</span>
                      <span>•</span>
                      <span>{outcome.unit}</span>
                    </div>
                    <p className="text-lg font-serif text-foreground mt-2">{outcome.outcome_text}</p>
                  </div>
                  <div className="flex-shrink-0 bg-primary/5 border border-primary/20 rounded-lg p-3 flex flex-col items-center justify-center min-w-32">
                    <Lightbulb className="h-5 w-5 text-secondary mb-1" />
                    <span className="text-xs font-bold text-primary uppercase tracking-wider text-center">{t.curriculum.bloomLevel}</span>
                    <span className="text-lg font-semibold text-primary capitalize">{outcome.bloom_level}</span>
                    {outcome.bloom_confidence && (
                      <span className="text-[10px] text-muted-foreground mt-1">
                        {(outcome.bloom_confidence * 100).toFixed(0)}% {t.curriculum.confidence}
                      </span>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <Card className="bg-muted/50 border-dashed">
          <CardContent className="flex flex-col items-center justify-center py-16 text-center">
            <Target className="h-12 w-12 text-muted-foreground/50 mb-4" />
            <h3 className="text-lg font-medium text-foreground">{t.curriculum.noOutcomesTitle}</h3>
            <p className="text-sm text-muted-foreground max-w-sm mt-2 mb-6">{t.curriculum.noOutcomesDesc}</p>
            <Button onClick={() => setIsDialogOpen(true)} variant="outline">{t.curriculum.addFirst}</Button>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
