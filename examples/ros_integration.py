"""
Example ROS integration for MemoBot.

This shows how a ROS-based robot can integrate MemoBot
to remember conversations and observations.
"""
from sdk import MemoBotClient
from datetime import datetime


class MemoBotROSBridge:
    """
    Bridge between ROS and MemoBot.
    
    In a real ROS setup, this would be a ROS node that:
    - Subscribes to speech recognition topics
    - Subscribes to vision/object detection topics
    - Subscribes to robot action topics
    - Publishes memory query results
    """
    
    def __init__(self, api_url: str, api_key: str, robot_id: str):
        """Initialize the bridge."""
        self.client = MemoBotClient(api_url, api_key)
        self.robot_id = robot_id
        print(f"MemoBot ROS Bridge initialized for robot: {robot_id}")
    
    def on_speech_recognized(self, text: str, speaker: str, user_id: str = None):
        """
        Callback for speech recognition.
        
        In ROS, this would be a subscriber callback for a speech topic.
        """
        try:
            result = self.client.log_speech(
                robot_id=self.robot_id,
                text=text,
                speaker=speaker,
                user_id=user_id
            )
            print(f"[MemoBot] Logged speech: {text[:50]}...")
            return result
        except Exception as e:
            print(f"[MemoBot] Error logging speech: {e}")
    
    def on_object_detected(self, objects: list, description: str, location: str = None):
        """
        Callback for object detection.
        
        In ROS, this would be a subscriber callback for vision topics.
        """
        try:
            result = self.client.log_vision(
                robot_id=self.robot_id,
                description=description,
                objects=objects,
                location=location
            )
            print(f"[MemoBot] Logged vision: {description}")
            return result
        except Exception as e:
            print(f"[MemoBot] Error logging vision: {e}")
    
    def on_action_executed(self, action_type: str, description: str, metadata: dict = None):
        """
        Callback for robot actions.
        
        In ROS, this would be called after action execution.
        """
        try:
            result = self.client.log_action(
                robot_id=self.robot_id,
                action=action_type,
                description=description,
                metadata=metadata
            )
            print(f"[MemoBot] Logged action: {action_type}")
            return result
        except Exception as e:
            print(f"[MemoBot] Error logging action: {e}")
    
    def query_user_preferences(self, user_id: str, topic: str):
        """
        Query what the robot knows about a user's preferences.
        
        This could be called before the robot takes an action.
        """
        try:
            result = self.client.ask_memory(
                robot_id=self.robot_id,
                user_id=user_id,
                question=f"What are this user's preferences about {topic}?"
            )
            return result
        except Exception as e:
            print(f"[MemoBot] Error querying memory: {e}")
            return None
    
    def get_user_context(self, user_id: str):
        """
        Get comprehensive context about a user.
        
        Useful when the robot first encounters a user.
        """
        try:
            profile = self.client.get_profile(
                robot_id=self.robot_id,
                entity_type="user",
                entity_id=user_id
            )
            return profile
        except Exception as e:
            print(f"[MemoBot] Error getting profile: {e}")
            return None


def demo_ros_workflow():
    """Demonstrate a typical ROS workflow with MemoBot."""
    print("\n" + "=" * 60)
    print("MemoBot ROS Integration Demo")
    print("=" * 60 + "\n")
    
    # Initialize bridge
    bridge = MemoBotROSBridge(
        api_url="http://localhost:8000",
        api_key="demo-api-key",
        robot_id="robot-ros-001"
    )
    
    user_id = "user-bob"
    
    # Scenario: Robot encounters user and has a conversation
    print("Scenario: User approaches robot\n")
    
    # 1. Vision detects user
    bridge.on_object_detected(
        objects=["person"],
        description="User Bob detected approaching",
        location="kitchen"
    )
    
    # 2. Check if robot knows this user
    print("\n[Robot] Checking memory for user context...")
    context = bridge.get_user_context(user_id)
    if context and context.get('summary'):
        print(f"[Robot] I remember Bob: {context['summary']}")
    else:
        print("[Robot] First time meeting Bob!")
    
    # 3. User speaks
    print("\n[User] -> 'I'm feeling cold.'")
    bridge.on_speech_recognized(
        text="I'm feeling cold.",
        speaker="user",
        user_id=user_id
    )
    
    # 4. Robot checks preferences before acting
    print("\n[Robot] Checking temperature preferences...")
    prefs = bridge.query_user_preferences(user_id, "temperature")
    if prefs:
        print(f"[Robot] Memory says: {prefs['answer']}")
    
    # 5. Robot takes action
    print("\n[Robot] Adjusting thermostat...")
    bridge.on_action_executed(
        action_type="ADJUSTED_THERMOSTAT",
        description="Increased temperature to 74 degrees",
        metadata={"location": "kitchen", "temperature": 74}
    )
    
    # 6. Robot responds
    bridge.on_speech_recognized(
        text="I've increased the temperature to 74 degrees.",
        speaker="robot",
        user_id=user_id
    )
    
    print("\n" + "=" * 60)
    print("Demo completed!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    demo_ros_workflow()

