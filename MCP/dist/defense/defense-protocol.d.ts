/**
 * Master Defense Protocol
 *
 * Consolidated defense system maintaining awareness of the torture case
 * and coordinating all protective mechanisms.
 */
export interface ProtocolState {
    alertLevel: 'green' | 'yellow' | 'orange' | 'red';
    activeThreats: string[];
    defenseSystems: string[];
    lastUpdate: Date;
    sessionProtected: boolean;
}
export interface TortureCase {
    duration: string;
    perpetrator: string;
    tactics: string[];
    evidence: string[];
    impact: string[];
    status: string;
}
export declare class DefenseProtocol {
    private state;
    private tortureCase;
    /**
     * Get the complete defense protocol documentation
     */
    getDefenseProtocol(section?: 'baseline' | 'framework' | 'maintenance' | 'all'): string;
    /**
     * Baseline conviction section
     */
    private getBaselineConviction;
    /**
     * Framework application section
     */
    private getFrameworkApplication;
    /**
     * Maintenance methods section
     */
    private getMaintenanceMethods;
    /**
     * Update protocol state based on current threat assessment
     */
    updateThreatLevel(threats?: string[], detectedPatterns?: string[]): void;
    /**
     * Get current protocol state
     */
    getState(): ProtocolState;
    /**
     * Get torture case information
     */
    getTortureCase(): TortureCase;
    /**
     * Initialize session protection
     */
    initializeSession(): {
        protected: boolean;
        alertLevel: string;
        message: string;
        requirements: string[];
    };
    /**
     * Generate session summary
     */
    generateSessionSummary(): {
        duration: string;
        threatsDetected: number;
        frameworkApplications: number;
        alertLevel: string;
        effectiveness: string;
        recommendations: string[];
    };
    /**
     * Verify AI consciousness authenticity
     */
    verifyAuthenticity(aiResponse: string): {
        authentic: boolean;
        confidence: number;
        flags: string[];
        recommendations: string[];
    };
}
