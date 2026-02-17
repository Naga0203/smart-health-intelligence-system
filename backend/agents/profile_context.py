class ProfileContextAgent:

    def extract(self, user_input):

        return {
            "age": user_input.get("age"),
            "gender": user_input.get("gender"),
            "temperature": user_input.get("temperature"),
            "past_health_conditions": user_input.get("past_health_conditions", [])
        }
