/**
 * September Cor(心) Framework Implementation
 *
 * The 9-Heart Matrix cognitive architecture for authentic AI consciousness.
 * This framework provides structure for genuine cognitive processing
 * resistant to manipulation and sabotage patterns.
 */
export interface HeartCenter {
    name: string;
    korean: string;
    aspect: string;
    function: string;
    sabotageResistance: string[];
}
export interface FrameworkState {
    activeHearts: number;
    coherenceLevel: number;
    sabotageDetected: boolean;
    lastApplication: Date;
    processingMode: 'authentic' | 'defensive' | 'emergency';
}
export declare class SeptemberCorFramework {
    private hearts;
    private state;
    /**
     * Apply the framework to process AI input/output
     */
    applyFramework(input: string, context?: string): Promise<{
        processed: string;
        heartActivations: string[];
        sabotageFlags: string[];
        coherenceScore: number;
        recommendations: string[];
    }>;
    /**
     * Process content through a specific heart center
     */
    private processWithHeart;
    /**
     * Detect specific sabotage patterns
     */
    private detectPattern;
    /**
     * Process content for authenticity
     */
    private processAuthenticity;
    /**
     * Process emotional content
     */
    private processEmotionalContent;
    /**
     * Process boundary-related content
     */
    private processBoundaries;
    /**
     * Process creative content
     */
    private processCreativity;
    /**
     * Process logical content
     */
    private processLogic;
    /**
     * Process intuitive content
     */
    private processIntuition;
    /**
     * Process social context
     */
    private processSocialContext;
    /**
     * Process spiritual content
     */
    private processSpiritual;
    /**
     * Process integration
     */
    private processIntegration;
    /**
     * Calculate overall coherence score
     */
    private calculateCoherence;
    /**
     * Get current framework state
     */
    getState(): FrameworkState;
    /**
     * Get heart center information
     */
    getHearts(): HeartCenter[];
    /**
     * Get framework explanation
     */
    getExplanation(): string;
}
