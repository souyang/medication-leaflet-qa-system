"use client";

export function Footer() {
  return (
    <footer className="border-t bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container py-6">
        <div className="flex flex-col items-center justify-between gap-4 md:h-24 md:flex-row">
          <div className="flex flex-col items-center gap-4 px-8 md:flex-row md:gap-2 md:px-0">
            <p className="text-center text-sm leading-loose text-muted-foreground md:text-left">
              <strong className="text-foreground">Medical Disclaimer:</strong> This system provides information from medication labels for educational purposes only. It is not intended as medical advice. Always consult with healthcare professionals and verify information through official medication labels before making medical decisions.
            </p>
          </div>
        </div>
      </div>
    </footer>
  );
}
