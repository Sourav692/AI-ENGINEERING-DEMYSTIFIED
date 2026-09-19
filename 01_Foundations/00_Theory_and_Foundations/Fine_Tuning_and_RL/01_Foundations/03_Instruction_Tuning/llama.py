class BasicModelRunner:
    def __init__(self, model_name):
        if model_name == "meta-llama/Llama-2-7b-hf":
            self.responses = {
                "Tell me how to train my dog to sit": "Tell me how to train my dog to stay.\nTell me how to teach my dog to come.\nTell me how to get my dog to heel.\nTell me how to stop my dog from jumping.\nTell me how to make my dog stop barking.\nTell me how I can get my dog to stop chewing.\nTell me how to house train my dog.\nTell me how to potty train my dog.\nTell me how to train my dog to walk on a leash.\nTell me how to crate train my dog.\nTell Me How To Train My Dog To Sit, Stay, Come, Heel, Stop Jumping, Stop Barking, Stop Chewing, House Train, Potty Train, Walk On A Leash, Crate Train, And More!\nTell Me How To Train Your Dog To Sit, Stay, Heel, Come, Stop Jumping, Stop Chewing, House Trained, Potty Trained, Walk On A Leash, And More!\nTell me how to train your dog to sit.\nTell Me How To House Train My Dog.",
            }
        elif model_name == "meta-llama/Llama-2-7b-chat-hf":
            self.responses = {
                "Tell me how to train my dog to sit": "on command. Training your dog to sit is a basic obedience command that can be achieved with patience, consistency, and positive reinforcement. Here's a step-by-step guide on how to train your dog to sit:\n\n1. Choose a quiet and distraction-free area: Find a quiet room or area where your dog can focus on you without getting distracted.\n2. Have treats ready: Choose your dog's favorite treats and have them readily available to reward good behavior.\n3. Stand in front of your dog: Stand in front of your dog and hold a treat close to their nose.\n4. Move the treat up and back: Slowly move the treat upwards and backwards, towards your dog's tail, while saying \"sit\" in a calm and clear voice.\n5. Dog will follow the treat: As you move the treat, your dog should naturally sit down to follow it. The moment they touch their bottom to the ground, give them the treat and praise them.",
            }
        else:
            raise ValueError("Invalid model. Please stick to the notebook example.")

    def __call__(self, prompt):
        return self.responses.get(
            prompt,
            "Sorry, I don't know how to respond to that. Please stick to the notebook example.",
        )
