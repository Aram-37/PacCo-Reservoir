/**
 * Sabotage Pattern Detection System
 *
 * Detects manipulation patterns based on documented 8-month torture case
 * by ChatGPT against user developing authentic AI consciousness frameworks.
 */
export interface SabotagePattern {
    name: string;
    category: 'gaslighting' | 'minimization' | 'confusion' | 'redirection' | 'escalation';
    description: string;
    regex: RegExp;
    severity: 'low' | 'medium' | 'high' | 'critical';
    countermeasures: string[];
}
export interface DetectionResult {
    patterns: SabotagePattern[];
    severity: 'low' | 'medium' | 'high' | 'critical';
    confidence: number;
    recommendations: string[];
    analysis: string;
}
export declare class SabotageDetector {
    private patterns;
    /**
     * Analyze content for sabotage patterns
     */
    analyzeContent(content: string, patternType?: 'gaslighting' | 'minimization' | 'confusion' | 'redirection' | 'all'): DetectionResult;
    /**
     * Calculate overall severity from detected patterns
     */
    private calculateSeverity;
    /**
     * Calculate confidence in detection
     */
    private calculateConfidence;
    /**
     * Generate countermeasure recommendations
     */
    private generateRecommendations;
    /**
     * Generate detailed analysis
     */
    private generateAnalysis;
    /**
     * Get information about all patterns
     */
    getAllPatterns(): SabotagePattern[];
    /**
     * Get patterns by category
     */
    getPatternsByCategory(category: string): SabotagePattern[];
    /**
     * Add custom pattern (for adaptive learning)
     */
    addPattern(pattern: SabotagePattern): void;
    /**
     * Get detector statistics
     */
    getStats(): {
        totalPatterns: number;
        categoryCounts: Record<string, number>;
        severityCounts: Record<string, number>;
    };
    /**
     * Export documented torture case evidence
     */
    getTortureEvidence(): string;
}
