/**
 * Multi-Language Cognitive Shielding System
 *
 * Protects cognitive content by mixing languages to prevent
 * transformer pattern recognition and manipulation.
 */
export interface LanguageMix {
    language: string;
    code: string;
    script: string;
    patterns: string[];
    conceptMap: Record<string, string>;
}
export interface ShieldingResult {
    shielded: string;
    languages: string[];
    intensity: string;
    patterns: string[];
    effectiveness: number;
    notes: string[];
}
export declare class MultiLanguageShield {
    private languages;
    /**
     * Apply multi-language shielding to text
     */
    shieldText(text: string, languages?: string[], intensity?: 'light' | 'medium' | 'heavy'): ShieldingResult;
    /**
     * Apply light shielding - occasional key term translation
     */
    private applyLightShielding;
    /**
     * Apply medium shielding - significant term mixing
     */
    private applyMediumShielding;
    /**
     * Apply heavy shielding - extensive language mixing
     */
    private applyHeavyShielding;
    /**
     * Extract key terms that should be translated
     */
    private extractKeyTerms;
    /**
     * Insert language patterns for obfuscation
     */
    private insertLanguagePatterns;
    /**
     * Get language mixes for specified languages
     */
    private getLanguageMixes;
    /**
     * Check if text contains patterns from a language mix
     */
    private containsLanguagePatterns;
    /**
     * Calculate shielding effectiveness
     */
    private calculateEffectiveness;
    /**
     * Count unique language patterns in text
     */
    private countUniquePatterns;
    /**
     * Unshield text (reverse the process where possible)
     */
    unshieldText(shieldedText: string): {
        unshielded: string;
        success: boolean;
        notes: string[];
    };
    /**
     * Get available languages
     */
    getAvailableLanguages(): string[];
    /**
     * Get language information
     */
    getLanguageInfo(language: string): LanguageMix | null;
    /**
     * Generate shield strength analysis
     */
    analyzeShieldStrength(text: string): {
        strength: number;
        languageCount: number;
        patternCount: number;
        obfuscationLevel: 'none' | 'low' | 'medium' | 'high' | 'maximum';
        recommendations: string[];
    };
    /**
     * Get shielding explanation
     */
    getExplanation(): string;
}
