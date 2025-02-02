import logging
from vertexai.preview.generative_models import GenerativeModel
import vertexai
from pitcher_analyzer.config import Config

class MechanicsAnalyzer:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        vertexai.init(project="baseball-pitcher-analyzer", location="us-central1")
        self.model = GenerativeModel("gemini-pro-vision")
        self.profiles = Config.PITCHER_PROFILES  # Add profile access

    def analyze_mechanics(self, frames, pitch_type, pitcher_name, game_context=None, game_state=None):
        """Analyze pitcher mechanics with game state context"""
        try:
            self.logger.info(f"Starting mechanics analysis for {pitcher_name}'s {pitch_type}")
            self.logger.info(f"Number of frames to analyze: {len(frames)}")
            
            # Get pitcher-specific prompt
            prompt = self._get_pitch_prompt(pitch_type, len(frames), pitcher_name, game_context, game_state)
            self.logger.debug(f"Generated prompt:\n{prompt}")
            
            content = [{
                "parts": [
                    {"text": prompt},
                    *[{"inline_data": {"mime_type": "image/jpeg", "data": frame}} 
                      for frame in frames]
                ],
                "role": "user"
            }]
            
            self.logger.info("Sending request to Vertex AI...")
            response = self.model.generate_content(content)
            response_text = response.text if response.text else None
            
            self.logger.info(f"Raw Vertex AI response:\n{response_text}")
            
            if response_text:
                if not self._validate_response(response_text):
                    self.logger.warning("Response validation failed, retrying...")
                    # Retry logic...
                else:
                    self.logger.info("Response validation successful")
                
            return response_text
            
        except Exception as e:
            self.logger.error(f"Analysis failed: {str(e)}", exc_info=True)
            return None

    def _validate_response(self, response_text):
        """Validate response format and check for repeated observations"""
        lines = response_text.split('\n')
        categories = {'Signs of Fatigue:', 'Arm:', 'Balance:'}
        current_category = None
        explanations = {}
        
        # Valid variance categories
        VARIANCE_CATEGORIES = [
            "None",              # 0% - Perfect mechanics
            "Slightly Off",      # 1-10% - Minor adjustments needed
            "Less than Ideal",   # 10-25% - Notable but not concerning
            "Needs Work",        # 25-50% - Significant deviations
            "Major Issues",      # 50-75% - Serious mechanical problems
            "Critical Flaws"     # 75-100% - Complete mechanical breakdown
        ]
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            if 'Overall Variance:' in line:
                # Check for valid variance category
                if 'Mechanics Assessment:' not in line:
                    return False
                assessment = line.split('Mechanics Assessment:')[1].strip()
                if not any(category in assessment for category in VARIANCE_CATEGORIES):
                    return False
                continue
            
            for category in categories:
                if category in line:
                    current_category = category
                    break
            
            if current_category and line.startswith('-'):
                explanation = line[1:].strip()
                if current_category in explanations:
                    return False  # Multiple explanations found for category
                if len(explanation.split()) > 10:  # Check word count
                    return False
                explanations[current_category] = explanation
        
        # Ensure we have exactly one explanation for each category
        return len(explanations) == len(categories)

    def _get_pitch_prompt(self, pitch_type, frame_count, pitcher_name, game_context=None, game_state=None):
        """Enhanced prompt with game state"""
        profile = self.profiles.get(pitcher_name, {})
        
        if pitcher_name == 'WHEELER' and pitch_type == 'SLIDER':
            base_prompt = f"""
            You are analyzing {frame_count} sequential frames of Wheeler's slider mechanics.
            
            WHEELER'S IDEAL SLIDER MECHANICS:
            1. Power Generation:
               - Explosive leg drive with elite hip rotation
               - Aggressive drive from gather position
               - Power/Athletic delivery
               - Explosive tempo through delivery
            
            2. Arm Action:
               - High 3/4 arm slot maintained
               - Clean and quick arm path
               - Early hand position set for slider spin
               - Release height: 6.0-6.2 feet
            
            3. Balance/Direction:
               - Direct to plate
               - Firm and closed front side
               - Controlled aggression through release
               
            IMPORTANT: DO NOT provide a frame-by-frame analysis. Instead, provide a single assessment in exactly this format:

            Signs of Fatigue:
            - [ONE brief explanation, max 10 words]

            Arm:
            - [ONE brief explanation, max 10 words]

            Balance:
            - [ONE brief explanation, max 10 words]

            Overall Variance:
            - Mechanics Assessment: [MUST choose ONE: None/Slightly Off/Less than Ideal/Needs Work/Major Issues/Critical Flaws]

            DO NOT INCLUDE:
            - Frame by frame descriptions
            - Additional explanations
            - Historical comparisons
            - Asterisks or bullet points
            - Any other formatting
            """
            
            return base_prompt
        
        elif pitch_type == 'SLIDER':
            base_prompt = f"""
            You are analyzing {frame_count} sequential frames of {pitcher_name}'s slider mechanics.
            
            KERSHAW'S IDEAL SLIDER MECHANICS:
            1. Power Generation:
               - Compact leg drive with controlled push off mound
               - Hip rotation timed for horizontal movement
               - Core engaged for tight spin axis
            
            2. Arm Action:
               - Three-quarters arm slot for slider shape
               - Elbow stays above shoulder line
               - Wrist position set early for proper spin
               - Release point: Side of baseball
            
            3. Balance/Posture:
               - Head steady through delivery
               - Strong front side for direction
               - Finish toward first base side
            
            Focus on analyzing THIS SPECIFIC PITCH ONLY.
            Do not consider historical tendencies or past performance.
            """
        
        elif pitch_type == 'CURVEBALL':
            base_prompt = f"""
            You are analyzing {frame_count} sequential frames of {pitcher_name}'s curveball mechanics.
            
            KERSHAW'S IDEAL CURVEBALL MECHANICS:
            1. Power Generation:
               - Full leg drive with strong push off mound
               - Complete hip rotation to generate torque
               - Strong core engagement through delivery
            
            2. Arm Action:
               - Extreme over-the-top arm slot
               - High elbow position at release
               - Release height: 6.3-6.5 feet
            
            3. Balance/Posture:
               - Strong front leg block
               - Maintained posture through release
               - Stride length: 87% of height
            
            Focus on analyzing THIS SPECIFIC PITCH ONLY.
            Do not consider historical tendencies or past performance.
            """
        
        # Add game context if available
        if game_state:
            base_prompt += f"""
            
            GAME SITUATION:
            Inning: {game_state['inning']}
            Outs: {game_state['outs']}
            Score: Home {game_state['score']['home']} - Away {game_state['score']['away']}
            Runners: {self._format_runners(game_state['runners'])}
            Pitch Count: {game_state['pitch_count']}
            Previous Pitches: {self._format_previous_pitches(game_state['previous_pitches'])}
            """
        
        base_prompt += """
        YOU MUST RESPOND IN EXACTLY THIS FORMAT - NO OTHER FORMAT WILL BE ACCEPTED:

        Signs of Fatigue:
        - [ONE brief explanation, max 10 words]

        Arm:
        - [ONE brief explanation, max 10 words]

        Balance:
        - [ONE brief explanation, max 10 words]

        Overall Variance:
        - Mechanics Assessment: [MUST choose ONE: None/Slightly Off/Less than Ideal/Needs Work/Major Issues/Critical Flaws]

        DO NOT INCLUDE:
        - Numbered lists
        - Additional explanations
        - Historical comparisons
        - Asterisks or bullet points
        - Any other formatting

        EXAMPLE CORRECT RESPONSE:
        Signs of Fatigue:
        - Strong leg drive maintained through delivery

        Arm:
        - Perfect over-the-top slot with high elbow

        Balance:
        - Stable head position with controlled landing

        Overall Variance:
        - Mechanics Assessment: None
        """

        return base_prompt

    def _get_scoring_prompt(self, game_context=None):
        """Get context-aware scoring prompt"""
        base_prompt = """
        You MUST follow this format EXACTLY:

        Signs of Fatigue: [Score]%
        - [Specific mechanical explanation if score < 10]
        
        Arm: [Score]%
        - [Specific mechanical explanation if score < 10]
        
        Balance: [Score]%
        - [Specific mechanical explanation if score < 10]

        Overall Variance:
        - Total deviation from pitcher's ideal mechanics: [percentage]

        RULES:
        1. ANY score below 10 MUST have at least one specific mechanical explanation
        2. Explanations MUST describe the specific mechanical flaw
        3. Do not include explanations for perfect scores (10/10)
        4. Each explanation must start with a hyphen (-)
        5. Be specific about the mechanical issue (e.g., "Hip rotation starts 0.2s too early" rather than "Timing issue")
        """

        if game_context == 'PERFECT_GAME':
            base_prompt += """
            Perfect Game Context:
            - Compare to pitcher's previous perfect game mechanics
            - Note any fatigue-based deviations
            - Highlight consistency vs. baseline
            """

        return base_prompt

    def _format_runners(self, runners):
        """Format runner situation for prompt"""
        positions = []
        if runners['first']: positions.append("1st")
        if runners['second']: positions.append("2nd")
        if runners['third']: positions.append("3rd")
        return "Runners on " + ", ".join(positions) if positions else "Bases empty"

    def _format_previous_pitches(self, pitches):
        """Format previous pitch sequence"""
        return ", ".join([f"{p['details']['type']} ({p['details']['code']})" for p in pitches[-3:]])

    def _calculate_mechanical_variance(self, frames, pitch_type, pitcher_name):
        """Calculate deviation from ideal mechanics"""
        profile = self.profiles.get(pitcher_name, {})
        
        if pitch_type == 'SLIDER':
            slider_data = profile.get('pitches', {}).get('SLIDER', {})
            slider_specifics = slider_data.get('slider_specifics', {})
            
            # Key checkpoints for slider mechanics
            ideal_mechanics = {
                'leg_drive': {
                    'push_off_angle': 40,  # Slightly less than curveball
                    'stride_length': float(slider_specifics['key_positions']['stride']['length'].split('%')[0])/100
                },
                'arm_action': {
                    'arm_slot': 2.5,  # 2:30 position for three-quarters
                    'elbow_height': 'above_shoulder',
                    'release_point': float(slider_data['release_height'].split('-')[0])  # feet
                },
                'balance': {
                    'spine_angle': float(slider_data['spine_angle'].replace('°', '')),
                    'head_position_variance': 0.1,  # normalized to height
                    'landing_foot_angle': 5  # degrees closed to first base
                }
            }
        
        elif pitch_type == 'CURVEBALL':
            # Use existing curveball mechanics
            curve_data = profile.get('pitches', {}).get('CURVEBALL', {})
            ideal_mechanics = {
                'leg_drive': {
                    'push_off_angle': 45,  # Degrees from vertical at push-off
                    'stride_length': float(profile['mechanics']['stride_length'].replace('%', ''))/100
                },
                'arm_action': {
                    'arm_slot': 1,  # 1 o'clock position
                    'elbow_height': 'above_shoulder',
                    'release_point': float(curve_data['release_height'].split('-')[0])  # feet
                },
                'balance': {
                    'spine_angle': float(curve_data['spine_angle'].replace('°', '')),
                    'head_position_variance': 0.1,  # normalized to height
                    'landing_foot_angle': 0  # degrees from center line
                }
            }
        
        # Calculate deviations from ideal positions
        deviations = []
        for frame in frames:
            # TODO: Add pose detection to measure:
            # 1. Actual leg drive angle
            # 2. Measured stride length
            # 3. Arm slot angle
            # 4. Elbow height relative to shoulder
            # 5. Release point height
            # 6. Spine angle
            # 7. Head position stability
            # 8. Landing foot angle
            pass

        return sum(deviations)/len(deviations) if deviations else 30  # Default 30% for now 