import { useState, useEffect } from 'react';
import { Button } from './ui/button';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogFooter } from './ui/dialog';
import { Badge } from './ui/badge';

interface OnboardingProps {
    onComplete: () => void;
}

export function OnboardingWizard({ onComplete }: OnboardingProps) {
    const [open, setOpen] = useState(false);
    const [step, setStep] = useState(0);

    useEffect(() => {
        const hasSeenOnboarding = localStorage.getItem('autoreflex-onboarding-completed');
        if (!hasSeenOnboarding) {
            setOpen(true);
        }
    }, []);

    const handleNext = () => {
        if (step < 3) {
            setStep(step + 1);
        } else {
            handleComplete();
        }
    };

    const handleComplete = () => {
        localStorage.setItem('autoreflex-onboarding-completed', 'true');
        setOpen(false);
        onComplete();
    };

    const steps = [
        {
            title: "Welcome to AutoReflex",
            description: "Your local Mission Control for autonomous coding agents. AutoReflex uses the OODA Loop (Observe, Orient, Decide, Act) to optimize and execute tasks with Claude Code.",
            badge: "Mission Start"
        },
        {
            title: "Step 1: Observe (Define)",
            description: "Start by describing your high-level goal in the 'Observation Phase' card. Be descriptive! The system will use this to 'Orient' itself.",
            badge: "Observe"
        },
        {
            title: "Step 2: Orient (Optimize)",
            description: "AutoReflex uses advanced prompting strategies (inspired by DSPy) to restructure your request into an optimized flight plan for the AI agent.",
            badge: "Orient"
        },
        {
            title: "Step 3: Act (Execute)",
            description: "Once approved, the agent executes the loop. You can watch its internal thought process and CLI outputs in real-time in the 'System Logs' panel.",
            badge: "Act"
        }
    ];

    return (
        <Dialog open={open} onOpenChange={(val) => !val && handleComplete()}>
            <DialogContent className="sm:max-w-md">
                <DialogHeader>
                    <div className="mb-2">
                        <Badge variant="outline">{steps[step].badge}</Badge>
                    </div>
                    <DialogTitle>{steps[step].title}</DialogTitle>
                    <DialogDescription className="pt-2">
                        {steps[step].description}
                    </DialogDescription>
                </DialogHeader>
                <DialogFooter className="flex justify-between sm:justify-between mt-4">
                    <div className="flex gap-1 mt-2 sm:mt-0">
                        {steps.map((_, i) => (
                            <div 
                                key={i} 
                                className={`h-1.5 w-8 rounded-full transition-colors ${i === step ? 'bg-blue-500' : 'bg-gray-800'}`}
                            />
                        ))}
                    </div>
                    <Button onClick={handleNext}>
                        {step === steps.length - 1 ? "Launch Mission Control" : "Next"}
                    </Button>
                </DialogFooter>
            </DialogContent>
        </Dialog>
    );
}
