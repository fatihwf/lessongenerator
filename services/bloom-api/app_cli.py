import asyncio
import os
import sys

# Ensure UTF-8 output on Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Ensure imports work from the current directory
sys.path.insert(0, os.path.dirname(__file__))

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt, IntPrompt
from rich.table import Table
from dotenv import load_dotenv

# Load env variables before importing config
load_dotenv()

from database import SessionLocal, init_db
from models import CurriculumItem, LearnerProfile
from cag.cache import context_cache
from rag.retriever import retrieve_chunks
from generation.generator import generate_lesson_content

console = Console()

def init():
    console.print("[bold green]Initializing database and seeding data...[/bold green]")
    init_db()
    
    # Run the seed function from main.py if needed
    try:
        from main import _seed_if_empty
        _seed_if_empty()
    except Exception as e:
        console.print(f"[yellow]Warning during seeding: {e}[/yellow]")

def list_outcomes(db):
    outcomes = db.query(CurriculumItem).all()
    table = Table(title="Available Curriculum Outcomes")
    table.add_column("ID", style="cyan", justify="right")
    table.add_column("Subject", style="magenta")
    table.add_column("Unit", style="green")
    table.add_column("Outcome", style="white")
    table.add_column("Bloom Level", style="yellow")
    
    for o in outcomes:
        table.add_row(str(o.id), o.subject, o.unit, o.outcome_text, o.bloom_level)
    
    console.print(table)
    return outcomes

def list_profiles(db):
    profiles = db.query(LearnerProfile).all()
    table = Table(title="Available Learner Profiles")
    table.add_column("ID", style="cyan", justify="right")
    table.add_column("Name", style="magenta")
    table.add_column("Grade", style="green")
    table.add_column("Proficiency", style="white")
    table.add_column("Style", style="yellow")
    
    for p in profiles:
        table.add_row(str(p.id), p.name, p.grade, p.proficiency_level, str(p.preferred_style))
    
    console.print(table)
    return profiles

async def generate(db, outcome_id: int, profile_id: int):
    outcome = db.query(CurriculumItem).filter(CurriculumItem.id == outcome_id).first()
    profile = db.query(LearnerProfile).filter(LearnerProfile.id == profile_id).first()
    
    if not outcome or not profile:
        console.print("[bold red]Error: Invalid outcome or profile ID.[/bold red]")
        return
        
    bloom_level = outcome.bloom_level
    
    console.print(f"\n[bold blue]1. Extracting Target Bloom Level:[/bold blue] {bloom_level.upper()}")
    
    console.print("[bold blue]2. Checking Context-Aware Generation (CAG) cache...[/bold blue]")
    teaching_context = context_cache.get(
        grade=outcome.grade,
        unit=outcome.unit,
        outcome_id=outcome.id,
        bloom_level=bloom_level,
        profile=profile,
    )
    if teaching_context:
        console.print("   [green]Cache HIT - Found pedagogical strategy.[/green]")
    else:
        console.print("   [yellow]Cache MISS - Will generate new pedagogical strategy.[/yellow]")

    console.print(f"[bold blue]3. Running Retrieval-Augmented Generation (RAG) for '{outcome.unit}'...[/bold blue]")
    rag_results = retrieve_chunks(
        db=db,
        query=f"{outcome.outcome_text} {outcome.unit}",
        bloom_level=bloom_level,
        subject=outcome.subject,
        grade=outcome.grade,
        top_k=5,
    )
    console.print(f"   [green]Retrieved {len(rag_results)} relevant chunks.[/green]")
    
    console.print("[bold blue]4. Generating Personalized Lesson via AI Engine...[/bold blue]")
    console.print(f"   (Model: OpenRouter, targetting: {outcome.subject} - {outcome.grade}. Grade)")
    
    with console.status("[bold green]AI is thinking...[/bold green]"):
        lesson_data = await generate_lesson_content(
            outcome=outcome,
            profile=profile,
            rag_chunks=rag_results,
            bloom_level=bloom_level,
            teaching_context=teaching_context,
        )

    if not teaching_context:
        new_context = {
            "outcome": outcome.outcome_text,
            "bloom_level": bloom_level,
            "grade": outcome.grade,
            "strategy": lesson_data.get("personalization_summary", {}),
        }
        context_cache.set(
            grade=outcome.grade,
            unit=outcome.unit,
            outcome_id=outcome.id,
            bloom_level=bloom_level,
            profile=profile,
            context=new_context,
        )

    console.print("\n[bold green]===== LESSON GENERATED SUCCESSFULLY =====[/bold green]\n")
    
    # Format and print the lesson
    title = lesson_data.get("lesson_title", "Untitled Lesson")
    console.print(Panel(f"[bold]{title}[/bold]", border_style="green"))
    
    pers = lesson_data.get("personalization_summary", {})
    if pers:
        console.print("[bold yellow]Personalization Summary:[/bold yellow]")
        for k, v in pers.items():
            console.print(f"  [cyan]{k}:[/cyan] {v}")
    
    sections = lesson_data.get("sections", {})
    
    def print_section(title, content):
        if not content: return
        console.print(f"\n[bold magenta]--- {title} ---[/bold magenta]")
        if isinstance(content, list):
            for item in content:
                console.print(f"• {item}")
        else:
            console.print(content)

    print_section("Introduction", sections.get("introduction"))
    print_section("Explanation", sections.get("explanation"))
    print_section("Examples", sections.get("examples"))
    print_section("Practice", sections.get("practice"))
    print_section("Misconceptions", sections.get("misconceptions"))
    print_section("Summary", sections.get("summary"))
    print_section("Assessment", sections.get("assessment"))
    
    sources = lesson_data.get("sources_used", [])
    if sources:
        print_section("Sources Used", sources)


async def main():
    console.print(Panel.fit("[bold cyan]Bloom-Aware Lesson Generator CLI[/bold cyan]\nLocal Execution Environment", border_style="cyan"))
    
    init()
    db = SessionLocal()
    try:
        while True:
            console.print("\n[bold]Main Menu[/bold]")
            console.print("1. List Curriculum Outcomes")
            console.print("2. List Learner Profiles")
            console.print("3. Generate Lesson")
            console.print("4. Exit")
            
            choice = Prompt.ask("Select an option", choices=["1", "2", "3", "4"])
            
            if choice == "1":
                list_outcomes(db)
            elif choice == "2":
                list_profiles(db)
            elif choice == "3":
                list_outcomes(db)
                list_profiles(db)
                
                o_id = IntPrompt.ask("Enter Curriculum Outcome ID")
                p_id = IntPrompt.ask("Enter Learner Profile ID")
                
                await generate(db, o_id, p_id)
            elif choice == "4":
                console.print("Goodbye!")
                break
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(main())
