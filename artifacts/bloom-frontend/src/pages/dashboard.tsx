import { Link } from "wouter";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useGetLessonStats, useListLessons } from "@workspace/api-client-react";
import { BookOpen, RefreshCw, FileText } from "lucide-react";
import { format } from "date-fns";
import { useT } from "@/i18n";

export default function Dashboard() {
  const { t } = useT();
  const { data: stats, isLoading: statsLoading } = useGetLessonStats();
  const { data: lessons, isLoading: lessonsLoading } = useListLessons();

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <h1 className="text-3xl font-serif font-bold tracking-tight text-primary">{t.dashboard.title}</h1>
          <p className="text-muted-foreground mt-1">{t.dashboard.subtitle}</p>
        </div>
        <Button asChild className="gap-2">
          <Link href="/generate">
            <RefreshCw className="h-4 w-4" />
            {t.dashboard.quickGenerate}
          </Link>
        </Button>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        <Card className="hover-elevate transition-all border-l-4 border-l-primary">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">{t.dashboard.totalLessons}</CardTitle>
          </CardHeader>
          <CardContent>
            {statsLoading ? (
              <div className="h-8 w-16 bg-muted animate-pulse rounded" />
            ) : (
              <div className="text-3xl font-bold">{stats?.total_lessons || 0}</div>
            )}
          </CardContent>
        </Card>

        <Card className="hover-elevate transition-all border-l-4 border-l-secondary">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">{t.dashboard.cacheHitRate}</CardTitle>
          </CardHeader>
          <CardContent>
            {statsLoading ? (
              <div className="h-8 w-16 bg-muted animate-pulse rounded" />
            ) : (
              <div className="text-3xl font-bold">{((stats?.cache_hit_rate || 0) * 100).toFixed(1)}%</div>
            )}
          </CardContent>
        </Card>

        <Card className="hover-elevate transition-all border-l-4 border-l-accent">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">{t.dashboard.avgSources}</CardTitle>
          </CardHeader>
          <CardContent>
            {statsLoading ? (
              <div className="h-8 w-16 bg-muted animate-pulse rounded" />
            ) : (
              <div className="text-3xl font-bold">{(stats?.avg_sources_used || 0).toFixed(1)}</div>
            )}
          </CardContent>
        </Card>
      </div>

      <div className="space-y-4">
        <h2 className="text-xl font-serif font-bold text-foreground flex items-center gap-2">
          <FileText className="h-5 w-5 text-primary" />
          {t.dashboard.recentLessons}
        </h2>

        {lessonsLoading ? (
          <div className="space-y-3">
            {[1, 2, 3].map(i => (
              <div key={i} className="h-24 bg-card rounded-lg border border-border animate-pulse" />
            ))}
          </div>
        ) : lessons && lessons.length > 0 ? (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {lessons.slice(0, 6).map(lesson => (
              <Card key={lesson.id} className="hover:border-primary/50 transition-colors">
                <CardHeader className="pb-2">
                  <div className="flex justify-between items-start">
                    <CardTitle className="text-base line-clamp-1" title={lesson.lesson_title}>
                      {lesson.lesson_title}
                    </CardTitle>
                  </div>
                  <CardDescription className="text-xs">
                    {format(new Date(lesson.created_at), "d MMM yyyy")}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center gap-2 text-sm text-muted-foreground mb-4">
                    <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-primary/10 text-primary">
                      {lesson.bloom_level}
                    </span>
                    <span>•</span>
                    <span>{lesson.subject}</span>
                  </div>
                  <Button variant="outline" size="sm" asChild className="w-full">
                    <Link href={`/lessons/${lesson.id}`}>
                      {t.dashboard.viewLesson}
                    </Link>
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
        ) : (
          <Card className="bg-muted/50 border-dashed">
            <CardContent className="flex flex-col items-center justify-center py-12 text-center">
              <BookOpen className="h-12 w-12 text-muted-foreground/50 mb-4" />
              <h3 className="text-lg font-medium text-foreground">{t.dashboard.noLessonsTitle}</h3>
              <p className="text-sm text-muted-foreground max-w-sm mt-2 mb-6">{t.dashboard.noLessonsDesc}</p>
              <Button asChild>
                <Link href="/generate">{t.dashboard.generateLesson}</Link>
              </Button>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
