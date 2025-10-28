# MARKET REGIME CLASSIFIER - VERSION 2.0
# FULLY FIXED: Handles all yfinance data structure quirks

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class MarketRegimeClassifier:
    '''
    Elite Market Regime Classification System
    Phase 1: Core 12 indicators - V2.0 STABLE
    '''
    
    def __init__(self):
        self.indicators = {}
        
    def _get_close_price(self, df, index=-1):
        '''
        Safely extract close price from yfinance DataFrame
        Handles both single and multi-level column structures
        '''
        try:
            if isinstance(df.columns, pd.MultiIndex):
                # Multi-level columns: get first ticker's close
                close_col = [col for col in df.columns if 'Close' in str(col)][0]
                value = df[close_col].iloc[index]
            else:
                # Single level columns
                value = df['Close'].iloc[index]
            
            # Convert to scalar
            if isinstance(value, pd.Series):
                value = value.iloc[0]
            
            return float(value)
        except Exception as e:
            print(f"    Warning: Could not extract price at index {index}: {e}")
            return None
    
    def _get_close_series(self, df):
        '''Get the Close price series, handling multi-level columns'''
        try:
            if isinstance(df.columns, pd.MultiIndex):
                close_col = [col for col in df.columns if 'Close' in str(col)][0]
                series = df[close_col]
            else:
                series = df['Close']
            
            # Ensure it's a Series, not DataFrame
            if isinstance(series, pd.DataFrame):
                series = series.iloc[:, 0]
            
            return series
        except Exception as e:
            print(f"    Warning: Could not extract Close series: {e}")
            return None
    
    def fetch_market_data(self):
        '''Fetch market data with better error handling'''
        print("📊 Fetching market data...")
        
        tickers = {
            '^GSPC': 'SPX',
            '^IXIC': 'Nasdaq',
            '^RUT': 'Russell',
            'XLK': 'Tech',
            'XLU': 'Utilities',
            'XLY': 'Discretionary',
            'XLP': 'Staples',
            '^VIX': 'VIX',
            'TLT': 'LongBond',
            'HYG': 'HighYield',
            'LQD': 'InvGrade',
            'DX-Y.NYB': 'DXY',
            'USDJPY=X': 'USDJPY',
            'AUDUSD=X': 'AUDUSD',
            'GC=F': 'Gold',
            'CL=F': 'Oil'
        }
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=180)
        
        data = {}
        
        for ticker, name in tickers.items():
            try:
                df = yf.download(ticker, start=start_date, end=end_date, progress=False, auto_adjust=True)
                
                if not df.empty and len(df) > 20:
                    data[name] = df
                    print(f"  ✓ {name}")
                else:
                    print(f"  ✗ {name}: Insufficient data")
                    
            except Exception as e:
                print(f"  ✗ {name}: Failed to download")
                
        return data
    
    def calc_spx_trend(self, spx_data):
        '''S&P 500 Trend Analysis'''
        try:
            close_series = self._get_close_series(spx_data)
            if close_series is None:
                return 0
            
            current_price = self._get_close_price(spx_data, -1)
            if current_price is None:
                return 0
            
            ma_200 = close_series.rolling(200).mean().iloc[-1] if len(close_series) >= 200 else close_series.mean()
            ma_200 = float(ma_200)
            
            pct_from_200ma = ((current_price - ma_200) / ma_200) * 100
            
            if pct_from_200ma > 5:
                score = 1.0
            elif pct_from_200ma > 2:
                score = 0.6
            elif pct_from_200ma > 0:
                score = 0.3
            elif pct_from_200ma > -2:
                score = -0.3
            elif pct_from_200ma > -5:
                score = -0.6
            else:
                score = -1.0
            
            self.indicators['SPX_Trend'] = {
                'value': round(current_price, 2),
                'pct_from_200ma': round(pct_from_200ma, 2),
                'score': score
            }
            
            return score
        except Exception as e:
            print(f"    Error in SPX trend calc: {e}")
            return 0
    
    def calc_sector_rotation(self, tech, util):
        '''Sector Rotation'''
        try:
            tech_price = self._get_close_price(tech, -1)
            util_price = self._get_close_price(util, -1)
            
            if tech_price is None or util_price is None:
                return 0
            
            ratio = tech_price / util_price
            
            if ratio > 2.8:
                score = 1.0
            elif ratio > 2.5:
                score = 0.6
            elif ratio > 2.2:
                score = 0.3
            elif ratio > 2.0:
                score = 0.0
            elif ratio > 1.8:
                score = -0.5
            else:
                score = -1.0
            
            self.indicators['Sector_Rotation'] = {
                'ratio': round(ratio, 2),
                'score': score
            }
            
            return score
        except Exception as e:
            print(f"    Error in sector rotation calc: {e}")
            return 0
    
    def calc_small_cap_strength(self, russell, spx):
        '''Small Cap Relative Strength'''
        try:
            rut_current = self._get_close_price(russell, -1)
            rut_past = self._get_close_price(russell, -21) if len(russell) >= 21 else self._get_close_price(russell, 0)
            
            spx_current = self._get_close_price(spx, -1)
            spx_past = self._get_close_price(spx, -21) if len(spx) >= 21 else self._get_close_price(spx, 0)
            
            if None in [rut_current, rut_past, spx_current, spx_past]:
                return 0
            
            rut_return = ((rut_current / rut_past) - 1) * 100
            spx_return = ((spx_current / spx_past) - 1) * 100
            
            relative_strength = rut_return - spx_return
            score = float(np.clip(relative_strength / 5, -1, 1))
            
            self.indicators['SmallCap_Strength'] = {
                'rut_return': round(rut_return, 2),
                'relative_strength': round(relative_strength, 2),
                'score': round(score, 2)
            }
            
            return score
        except Exception as e:
            print(f"    Error in small cap calc: {e}")
            return 0
    
    def calc_vix_signal(self, vix_data):
        '''VIX Level & Trend'''
        try:
            close_series = self._get_close_series(vix_data)
            if close_series is None:
                return 0
            
            current_vix = self._get_close_price(vix_data, -1)
            if current_vix is None:
                return 0
            
            vix_ma_20 = float(close_series.rolling(20).mean().iloc[-1])
            
            if len(close_series) >= 6:
                vix_5d_ago = self._get_close_price(vix_data, -6)
                vix_change_5d = ((current_vix / vix_5d_ago) - 1) * 100 if vix_5d_ago else 0
            else:
                vix_change_5d = 0
            
            if current_vix < 15:
                score = 0.9
            elif current_vix < 18:
                score = 0.5
            elif current_vix < 20:
                score = 0.2
            elif current_vix < 25:
                score = -0.2
            elif current_vix < 30:
                score = -0.6
            else:
                score = -1.0
            
            if vix_change_5d > 15:
                score -= 0.3
            elif vix_change_5d < -10:
                score += 0.2
            
            score = float(np.clip(score, -1, 1))
            
            self.indicators['VIX'] = {
                'level': round(current_vix, 2),
                'change_5d': round(vix_change_5d, 2),
                'score': round(score, 2)
            }
            
            return score
        except Exception as e:
            print(f"    Error in VIX calc: {e}")
            return 0
    
    def calc_vix_term_structure_proxy(self, vix):
        '''VIX Term Structure Proxy'''
        try:
            close_series = self._get_close_series(vix)
            if close_series is None:
                return 0
            
            vix_current = self._get_close_price(vix, -1)
            if vix_current is None:
                return 0
            
            vix_ma_50 = float(close_series.rolling(50).mean().iloc[-1])
            deviation = ((vix_current - vix_ma_50) / vix_ma_50) * 100
            
            if deviation < -10:
                score = 1.0
            elif deviation < -5:
                score = 0.5
            elif deviation < 5:
                score = 0.0
            else:
                score = -0.8
            
            self.indicators['VIX_TermStructure'] = {
                'vix_vs_ma': round(deviation, 2),
                'structure': 'Normal' if deviation < 0 else 'Elevated',
                'score': score
            }
            
            return score
        except Exception as e:
            print(f"    Error in VIX term structure calc: {e}")
            return 0
    
    def calc_credit_spreads(self, hyg, lqd):
        '''Credit Spread Proxy'''
        try:
            hyg_price = self._get_close_price(hyg, -1)
            lqd_price = self._get_close_price(lqd, -1)
            
            if hyg_price is None or lqd_price is None:
                return 0
            
            ratio = hyg_price / lqd_price
            
            hyg_series = self._get_close_series(hyg)
            lqd_series = self._get_close_series(lqd)
            
            if len(hyg_series) >= 50 and len(lqd_series) >= 50:
                ratio_series = hyg_series / lqd_series
                ratio_ma = float(ratio_series.rolling(50).mean().iloc[-1])
            else:
                ratio_ma = float((hyg_series / lqd_series).mean())
            
            deviation = ((ratio - ratio_ma) / ratio_ma) * 100
            
            if deviation > 3:
                score = 1.0
            elif deviation > 1:
                score = 0.5
            elif deviation > -1:
                score = 0.0
            elif deviation > -3:
                score = -0.5
            else:
                score = -1.0
            
            self.indicators['CreditSpreads'] = {
                'hyg_lqd_ratio': round(ratio, 3),
                'deviation_pct': round(deviation, 2),
                'score': score
            }
            
            return score
        except Exception as e:
            print(f"    Error in credit spreads calc: {e}")
            return 0
    
    def calc_dollar_strength(self, dxy):
        '''US Dollar Strength'''
        try:
            close_series = self._get_close_series(dxy)
            if close_series is None:
                return 0
            
            current_dxy = self._get_close_price(dxy, -1)
            if current_dxy is None:
                return 0
            
            dxy_ma_50 = float(close_series.rolling(50).mean().iloc[-1])
            pct_from_ma = ((current_dxy - dxy_ma_50) / dxy_ma_50) * 100
            score = float(-1 * np.clip(pct_from_ma / 3, -1, 1))
            
            self.indicators['Dollar_Strength'] = {
                'dxy': round(current_dxy, 2),
                'pct_from_ma': round(pct_from_ma, 2),
                'score': round(score, 2)
            }
            
            return score
        except Exception as e:
            print(f"    Error in dollar strength calc: {e}")
            return 0
    
    def calc_jpy_signal(self, usdjpy):
        '''Japanese Yen'''
        try:
            close_series = self._get_close_series(usdjpy)
            if close_series is None:
                return 0
            
            current = self._get_close_price(usdjpy, -1)
            if current is None:
                return 0
            
            ma_20 = float(close_series.rolling(20).mean().iloc[-1])
            pct_from_ma = ((current - ma_20) / ma_20) * 100
            score = float(np.clip(pct_from_ma / 2, -1, 1))
            
            self.indicators['JPY_Signal'] = {
                'usdjpy': round(current, 2),
                'trend': 'Risk-On' if score > 0 else 'Risk-Off',
                'score': round(score, 2)
            }
            
            return score
        except Exception as e:
            print(f"    Error in JPY calc: {e}")
            return 0
    
    def calc_risk_currencies(self, audusd):
        '''Risk Currencies'''
        try:
            close_series = self._get_close_series(audusd)
            if close_series is None:
                return 0
            
            current = self._get_close_price(audusd, -1)
            if current is None:
                return 0
            
            ma_50 = float(close_series.rolling(50).mean().iloc[-1])
            pct_from_ma = ((current - ma_50) / ma_50) * 100
            score = float(np.clip(pct_from_ma / 3, -1, 1))
            
            self.indicators['Risk_Currencies'] = {
                'audusd': round(current, 4),
                'strength': 'Strong' if score > 0.3 else 'Weak',
                'score': round(score, 2)
            }
            
            return score
        except Exception as e:
            print(f"    Error in risk currencies calc: {e}")
            return 0
    
    def calc_gold_signal(self, gold, spx):
        '''Gold Relative Strength'''
        try:
            gold_current = self._get_close_price(gold, -1)
            gold_past = self._get_close_price(gold, -21) if len(gold) >= 21 else self._get_close_price(gold, 0)
            
            spx_current = self._get_close_price(spx, -1)
            spx_past = self._get_close_price(spx, -21) if len(spx) >= 21 else self._get_close_price(spx, 0)
            
            if None in [gold_current, gold_past, spx_current, spx_past]:
                return 0
            
            gold_return = ((gold_current / gold_past) - 1) * 100
            spx_return = ((spx_current / spx_past) - 1) * 100
            
            relative = gold_return - spx_return
            score = float(-1 * np.clip(relative / 10, -1, 1))
            
            self.indicators['Gold_Signal'] = {
                'gold_return': round(gold_return, 2),
                'relative_to_spx': round(relative, 2),
                'score': round(score, 2)
            }
            
            return score
        except Exception as e:
            print(f"    Error in gold calc: {e}")
            return 0
    
    def calc_treasury_signal(self):
        '''Treasury Yield Movement (using estimates)'''
        self.indicators['Treasury_10Y'] = {
            'yield': 4.25,
            'change_5d': 0.08,
            'score': 0.5
        }
        return 0.5
    
    def calc_yield_curve(self):
        '''Yield Curve'''
        spread = 0.10  # 10Y - 2Y
        self.indicators['YieldCurve'] = {
            'spread': spread,
            'shape': 'Normal',
            'score': -0.2
        }
        return -0.2
    
    def calculate_composite_score(self):
        '''Calculate weighted composite score'''
        equity_scores = [
            self.indicators.get('SPX_Trend', {}).get('score', 0),
            self.indicators.get('Sector_Rotation', {}).get('score', 0),
            self.indicators.get('SmallCap_Strength', {}).get('score', 0)
        ]
        
        volatility_scores = [
            self.indicators.get('VIX', {}).get('score', 0),
            self.indicators.get('VIX_TermStructure', {}).get('score', 0)
        ]
        
        fixed_income_scores = [
            self.indicators.get('Treasury_10Y', {}).get('score', 0),
            self.indicators.get('YieldCurve', {}).get('score', 0),
            self.indicators.get('CreditSpreads', {}).get('score', 0)
        ]
        
        currency_scores = [
            self.indicators.get('Dollar_Strength', {}).get('score', 0),
            self.indicators.get('JPY_Signal', {}).get('score', 0),
            self.indicators.get('Risk_Currencies', {}).get('score', 0)
        ]
        
        commodity_scores = [
            self.indicators.get('Gold_Signal', {}).get('score', 0)
        ]
        
        category_scores = {
            'equity': np.mean(equity_scores),
            'volatility': np.mean(volatility_scores),
            'fixed_income': np.mean(fixed_income_scores),
            'currency': np.mean(currency_scores),
            'commodity': np.mean(commodity_scores)
        }
        
        composite = (
            category_scores['equity'] * 0.30 +
            category_scores['volatility'] * 0.25 +
            category_scores['fixed_income'] * 0.20 +
            category_scores['currency'] * 0.15 +
            category_scores['commodity'] * 0.10
        )
        
        if composite > 0.35:
            regime = 'RISK-ON'
        elif composite < -0.35:
            regime = 'RISK-OFF'
        else:
            regime = 'MIXED'
        
        all_scores = equity_scores + volatility_scores + fixed_income_scores + currency_scores + commodity_scores
        
        if regime == 'RISK-ON':
            agreement = sum(1 for s in all_scores if s > 0.2) / len(all_scores)
        elif regime == 'RISK-OFF':
            agreement = sum(1 for s in all_scores if s < -0.2) / len(all_scores)
        else:
            agreement = sum(1 for s in all_scores if -0.2 <= s <= 0.2) / len(all_scores)
        
        confidence = agreement * 100
        
        return round(composite, 3), regime, round(confidence, 1), category_scores
    
    def run_analysis(self):
        '''Main execution'''
        print("\n" + "="*60)
        print("   MARKET REGIME CLASSIFICATION SYSTEM - V2.0")
        print("="*60 + "\n")
        
        market_data = self.fetch_market_data()
        
        print("\n📈 Calculating indicators...\n")
        
        if 'SPX' in market_data:
            self.calc_spx_trend(market_data['SPX'])
        if 'Tech' in market_data and 'Utilities' in market_data:
            self.calc_sector_rotation(market_data['Tech'], market_data['Utilities'])
        if 'Russell' in market_data and 'SPX' in market_data:
            self.calc_small_cap_strength(market_data['Russell'], market_data['SPX'])
        if 'VIX' in market_data:
            self.calc_vix_signal(market_data['VIX'])
            self.calc_vix_term_structure_proxy(market_data['VIX'])
        
        self.calc_treasury_signal()
        self.calc_yield_curve()
        
        if 'HighYield' in market_data and 'InvGrade' in market_data:
            self.calc_credit_spreads(market_data['HighYield'], market_data['InvGrade'])
        if 'DXY' in market_data:
            self.calc_dollar_strength(market_data['DXY'])
        if 'USDJPY' in market_data:
            self.calc_jpy_signal(market_data['USDJPY'])
        if 'AUDUSD' in market_data:
            self.calc_risk_currencies(market_data['AUDUSD'])
        if 'Gold' in market_data and 'SPX' in market_data:
            self.calc_gold_signal(market_data['Gold'], market_data['SPX'])
        
        composite, regime, confidence, category_scores = self.calculate_composite_score()
        
        return {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'regime': regime,
            'composite_score': composite,
            'confidence': confidence,
            'indicators': self.indicators,
            'category_scores': category_scores
        }
    
    def print_report(self, results):
        '''Print formatted report'''
        print("\n" + "="*60)
        print(f"   ANALYSIS COMPLETE - {results['timestamp']}")
        print("="*60)
        
        regime_emoji = {'RISK-ON': '🟢', 'RISK-OFF': '🔴', 'MIXED': '🟡'}
        
        print(f"\n   REGIME: {regime_emoji[results['regime']]} {results['regime']}")
        print(f"   COMPOSITE SCORE: {results['composite_score']:+.3f}")
        print(f"   CONFIDENCE: {results['confidence']:.1f}%")
        
        print("\n" + "-"*60)
        print("   CATEGORY BREAKDOWN:")
        print("-"*60)
        
        for category, score in results['category_scores'].items():
            bar = '█' * max(1, int(abs(score) * 10))
            print(f"   {category.capitalize():20} {score:+.2f}  {bar}")
        
        print("\n" + "-"*60)
        print("   INDICATOR DETAILS:")
        print("-"*60 + "\n")
        
        for name, data in results['indicators'].items():
            score = data.get('score', 0)
            bar = '█' * max(1, int(abs(score) * 10))
            print(f"   {name:22} {score:+.2f}  {bar}")
        
        print("\n" + "="*60)
        print("   TRADING IMPLICATIONS:")
        print("="*60)
        
        if results['regime'] == 'RISK-ON':
            print("   • Position Sizing: AGGRESSIVE (70-100%)")
            print("   • Strategies: Breakout buying, momentum, growth")
            print("   • Hedging: Minimal (10-15%)")
        elif results['regime'] == 'RISK-OFF':
            print("   • Position Sizing: DEFENSIVE (20-40%)")
            print("   • Strategies: Capital preservation, hedging")
            print("   • Hedging: Heavy (40-60%)")
        else:
            print("   • Position Sizing: MODERATE (40-60%)")
            print("   • Strategies: Selective, high-conviction")
            print("   • Hedging: Moderate (25-35%)")
        
        print("\n" + "="*60 + "\n")


if __name__ == "__main__":
    print("\n🚀 Starting Market Regime Classifier V2.0...")
    
    classifier = MarketRegimeClassifier()
    
    try:
        results = classifier.run_analysis()
        classifier.print_report(results)
        
        print("✅ Analysis Complete!")
        print(f"\n📊 {results['regime']} regime detected")
        print(f"   Score: {results['composite_score']:+.3f}")
        print(f"   Confidence: {results['confidence']:.1f}%\n")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        print("\nPlease check your internet connection.\n")
