import { useState } from "react";
import { useListProfiles, useCreateProfile } from "@workspace/api-client-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger,
} from "@/components/ui/dialog";
import { Users, Plus, GraduationCap } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { useT } from "@/i18n";

export default function Profiles() {
  const { data: profiles, isLoading, refetch } = useListProfiles();
  const createProfile = useCreateProfile();
  const { toast } = useToast();
  const { t } = useT();

  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [formData, setFormData] = useState({
    name: "", grade: "", proficiency_level: "", reading_level: "", preferred_style: "",
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    createProfile.mutate(
      { data: { ...formData, weak_topics: [], strong_topics: [] } },
      {
        onSuccess: () => {
          toast({ title: t.profiles.successTitle, description: t.profiles.successDesc });
          setIsDialogOpen(false);
          setFormData({ name: "", grade: "", proficiency_level: "", reading_level: "", preferred_style: "" });
          refetch();
        },
        onError: () => {
          toast({ title: t.profiles.errorTitle, description: t.profiles.errorDesc, variant: "destructive" });
        }
      }
    );
  };

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <h1 className="text-3xl font-serif font-bold tracking-tight text-primary">{t.profiles.title}</h1>
          <p className="text-muted-foreground mt-1">{t.profiles.subtitle}</p>
        </div>

        <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
          <DialogTrigger asChild>
            <Button className="gap-2"><Plus className="h-4 w-4" />{t.profiles.addProfile}</Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>{t.profiles.dialogTitle}</DialogTitle>
              <DialogDescription>{t.profiles.dialogDesc}</DialogDescription>
            </DialogHeader>
            <form onSubmit={handleSubmit} className="space-y-4 pt-4">
              <div className="space-y-2">
                <Label htmlFor="name">{t.profiles.name}</Label>
                <Input id="name" required value={formData.name}
                  onChange={e => setFormData({...formData, name: e.target.value})}
                  placeholder={t.profiles.namePlaceholder} />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="grade">{t.profiles.grade}</Label>
                  <Input id="grade" required value={formData.grade}
                    onChange={e => setFormData({...formData, grade: e.target.value})}
                    placeholder={t.profiles.gradePlaceholder} />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="proficiency">{t.profiles.proficiency}</Label>
                  <Input id="proficiency" required value={formData.proficiency_level}
                    onChange={e => setFormData({...formData, proficiency_level: e.target.value})}
                    placeholder={t.profiles.proficiencyPlaceholder} />
                </div>
              </div>
              <div className="space-y-2">
                <Label htmlFor="style">{t.profiles.style}</Label>
                <Input id="style" value={formData.preferred_style}
                  onChange={e => setFormData({...formData, preferred_style: e.target.value})}
                  placeholder={t.profiles.stylePlaceholder} />
              </div>
              <Button type="submit" className="w-full" disabled={createProfile.isPending}>
                {createProfile.isPending ? t.profiles.creating : t.profiles.createButton}
              </Button>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      {isLoading ? (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {[1,2,3].map(i => (
            <div key={i} className="h-48 bg-card rounded-lg border border-border animate-pulse" />
          ))}
        </div>
      ) : profiles && profiles.length > 0 ? (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {profiles.map(profile => (
            <Card key={profile.id} className="hover:border-primary/50 transition-colors">
              <CardHeader className="pb-3">
                <CardTitle className="text-xl">{profile.name}</CardTitle>
                <CardDescription className="flex items-center gap-2">
                  <GraduationCap className="h-4 w-4" />
                  {t.common.grade} {profile.grade}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3 text-sm">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">{t.profiles.proficiencyLabel}</span>
                    <span className="font-medium">{profile.proficiency_level}</span>
                  </div>
                  {profile.preferred_style && (
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">{t.profiles.styleLabel}</span>
                      <span className="font-medium">{profile.preferred_style}</span>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <Card className="bg-muted/50 border-dashed">
          <CardContent className="flex flex-col items-center justify-center py-16 text-center">
            <Users className="h-12 w-12 text-muted-foreground/50 mb-4" />
            <h3 className="text-lg font-medium text-foreground">{t.profiles.noProfilesTitle}</h3>
            <p className="text-sm text-muted-foreground max-w-sm mt-2 mb-6">{t.profiles.noProfilesDesc}</p>
            <Button onClick={() => setIsDialogOpen(true)} variant="outline">{t.profiles.createFirst}</Button>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
