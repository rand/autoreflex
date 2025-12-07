import { render, screen, fireEvent } from '@testing-library/react';
import { OnboardingWizard } from '../components/Onboarding';
import { HelpContext } from '../components/HelpContext';

describe('OnboardingWizard', () => {
    beforeEach(() => {
        localStorage.clear();
    });

    it('renders the welcome step initially', () => {
        render(<OnboardingWizard onComplete={() => {}} />);
        expect(screen.getByText('Welcome to AutoReflex')).toBeInTheDocument();
        expect(screen.getByText('Mission Start')).toBeInTheDocument();
    });

    it('navigates through steps', () => {
        render(<OnboardingWizard onComplete={() => {}} />);
        
        const nextButton = screen.getByText('Next');
        
        // Step 1
        fireEvent.click(nextButton);
        expect(screen.getByText('Step 1: Observe (Define)')).toBeInTheDocument();
        
        // Step 2
        fireEvent.click(nextButton);
        expect(screen.getByText('Step 2: Orient (Optimize)')).toBeInTheDocument();
        
        // Step 3
        fireEvent.click(nextButton);
        expect(screen.getByText('Step 3: Act (Execute)')).toBeInTheDocument();
        
        // Finish
        const finishButton = screen.getByText('Launch Mission Control');
        expect(finishButton).toBeInTheDocument();
    });
});

describe('HelpContext', () => {
    it('renders the help trigger', () => {
        render(<HelpContext topic="Test Topic" description="Test Description" />);
        expect(screen.getByRole('button')).toBeInTheDocument();
    });
    
    // Testing popover content usually requires user interaction which we can simulate
    // but basic rendering test is sufficient for now.
});
