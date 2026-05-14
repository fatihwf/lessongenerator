import { Link, useLocation } from "wouter";
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuItem,
  SidebarMenuButton,
  SidebarProvider,
  SidebarTrigger
} from "@/components/ui/sidebar";
import { BookOpen, BrainCircuit, FileText, Home, Library, Target, Users } from "lucide-react";
import { useT, type Lang } from "@/i18n";

function LangSwitch() {
  const { lang, setLang } = useT();
  return (
    <div className="flex items-center gap-1 rounded-lg border border-sidebar-border bg-sidebar-accent/30 p-0.5 text-xs font-medium">
      {(["tr", "en"] as Lang[]).map((l) => (
        <button
          key={l}
          onClick={() => setLang(l)}
          className={`px-2.5 py-1 rounded-md transition-colors ${
            lang === l
              ? "bg-sidebar-primary text-sidebar-primary-foreground shadow-sm"
              : "text-sidebar-muted-foreground hover:text-sidebar-foreground"
          }`}
          aria-label={l === "tr" ? "Türkçe" : "English"}
        >
          {l.toUpperCase()}
        </button>
      ))}
    </div>
  );
}

export default function Layout({ children }: { children: React.ReactNode }) {
  const [location] = useLocation();
  const { t } = useT();

  return (
    <SidebarProvider>
      <div className="flex min-h-screen w-full bg-background">
        <Sidebar className="border-r border-sidebar-border">
          <SidebarHeader className="p-4">
            <div className="flex items-center justify-between gap-2">
              <div className="flex items-center gap-2 font-serif text-lg font-bold text-sidebar-foreground">
                <BrainCircuit className="h-5 w-5 text-secondary" />
                <span>BloomGen</span>
              </div>
              <LangSwitch />
            </div>
          </SidebarHeader>
          <SidebarContent>
            <SidebarMenu>
              <SidebarMenuItem>
                <SidebarMenuButton asChild isActive={location === "/"}>
                  <Link href="/"><Home className="h-4 w-4" /><span>{t.nav.dashboard}</span></Link>
                </SidebarMenuButton>
              </SidebarMenuItem>
              <SidebarMenuItem>
                <SidebarMenuButton asChild isActive={location === "/generate"}>
                  <Link href="/generate"><FileText className="h-4 w-4" /><span>{t.nav.generate}</span></Link>
                </SidebarMenuButton>
              </SidebarMenuItem>
              <SidebarMenuItem>
                <SidebarMenuButton asChild isActive={location.startsWith("/lessons") && location !== "/generate"}>
                  <Link href="/lessons"><BookOpen className="h-4 w-4" /><span>{t.nav.lessons}</span></Link>
                </SidebarMenuButton>
              </SidebarMenuItem>
              <SidebarMenuItem>
                <SidebarMenuButton asChild isActive={location === "/profiles"}>
                  <Link href="/profiles"><Users className="h-4 w-4" /><span>{t.nav.profiles}</span></Link>
                </SidebarMenuButton>
              </SidebarMenuItem>
              <SidebarMenuItem>
                <SidebarMenuButton asChild isActive={location === "/curriculum"}>
                  <Link href="/curriculum"><Target className="h-4 w-4" /><span>{t.nav.curriculum}</span></Link>
                </SidebarMenuButton>
              </SidebarMenuItem>
              <SidebarMenuItem>
                <SidebarMenuButton asChild isActive={location === "/knowledge"}>
                  <Link href="/knowledge"><Library className="h-4 w-4" /><span>{t.nav.knowledge}</span></Link>
                </SidebarMenuButton>
              </SidebarMenuItem>
              <SidebarMenuItem>
                <SidebarMenuButton asChild isActive={location === "/classify"}>
                  <Link href="/classify"><BrainCircuit className="h-4 w-4" /><span>{t.nav.classify}</span></Link>
                </SidebarMenuButton>
              </SidebarMenuItem>
            </SidebarMenu>
          </SidebarContent>
          <SidebarFooter className="p-4 text-xs text-sidebar-muted-foreground">
            v1.0.0 Scholarly Edit
          </SidebarFooter>
        </Sidebar>

        <div className="flex-1 flex flex-col min-w-0">
          <header className="h-14 border-b flex items-center justify-between px-4 md:hidden">
            <div className="flex items-center gap-2">
              <SidebarTrigger />
              <span className="ml-2 font-serif font-bold">BloomGen</span>
            </div>
            <LangSwitch />
          </header>
          <main className="flex-1 p-6 md:p-8 lg:p-12 max-w-7xl mx-auto w-full">
            {children}
          </main>
        </div>
      </div>
    </SidebarProvider>
  );
}
