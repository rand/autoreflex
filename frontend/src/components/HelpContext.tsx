import { HelpCircle } from 'lucide-react';
import { Popover, PopoverContent, PopoverTrigger } from './ui/popover';
import { Button } from './ui/button';

interface HelpContextProps {
    topic: string;
    description: string;
}

export function HelpContext({ topic, description }: HelpContextProps) {
    return (
        <Popover>
            <PopoverTrigger asChild>
                <Button variant="ghost" className="h-6 w-6 p-0 rounded-full hover:bg-gray-800 text-gray-500">
                    <HelpCircle className="h-4 w-4" />
                    <span className="sr-only">Help</span>
                </Button>
            </PopoverTrigger>
            <PopoverContent className="w-80">
                <div className="grid gap-2">
                    <h4 className="font-medium leading-none text-blue-400">{topic}</h4>
                    <p className="text-sm text-gray-400">
                        {description}
                    </p>
                </div>
            </PopoverContent>
        </Popover>
    );
}
