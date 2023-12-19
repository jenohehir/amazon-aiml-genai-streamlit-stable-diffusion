import streamlit as st
import glib as glib
from io import BytesIO

# def check_password():
#     """Returns `True` if the user had the correct password."""

#     def password_entered():
#         """Checks whether a password entered by the user is correct."""
#         if st.session_state["password"] == st.secrets["password"]:
#             st.session_state["password_correct"] = True
#             # del st.session_state["password"]  # don't store password
#         else:
#             st.session_state["password_correct"] = False

#     if "password_correct" not in st.session_state:
#         # First run, show input for password.
#         st.text_input(
#             "Password", type="password", on_change=password_entered, key="password"
#         )
#         return False
#     elif not st.session_state["password_correct"]:
#         # Password not correct, show input + error.
#         st.text_input(
#             "Password", type="password", on_change=password_entered, key="password"
#         )
#         st.error("😕 Password incorrect")
#         return False
#     else:
#         # Password correct.
        # return True

def s3_uploader(checkbox, filename, filebytes):
    if checkbox:
        glib.uploadFileToS3(filename, filebytes)
    st.session_state.filename = ''

some_prompts = {
    "Default" : "Type or Select a prompt from the dropdown. Something like - pencil sketch of pizza and some cake. You can edit any of the predefined prompts too, like changing from person to dog",
    "Paint Me": "A person in 8k resolution, photorealistic masterpiece by Aaron Horkey and Jeremy Mann, intricately detailed fluid gouache painting by Jean Baptiste, professional photography, natural lighting, volumetric lighting, maximalist, concept art, intricately detailed, complex, elegant, expansive cover",
    "Anime Style": "Anime style",
    "Anime Style - More Prompting": " Anime-inspired person in a vibrant cityscape, vivid colors, anime aesthetic, expressive eyes, colorful and dynamic palette, positive mood, anticipation and curiosity, visually engaging, cinematic framing",
    "DevOps Engineer": "A devops engineer, deep coding expertise, cloud, cloud expertise, automation, it, information technology, programming, clean, crisp",
    "Impressionist Portrait": "portrait in an Impressionist style, vague, colorful, bright",
    "Portrait Photo": "Portrait photo side profile, looking away, serious eyes, 50mm portrait photography, hard rim lighting photography–beta –ar 2:3 –beta –upbeta",
    "Like a Lawyer": "High Quality, Intricately Detailed, Hyper-Realistic Lawyer Portrait Photography, Volumetric Lighting, Full Character, 4k, In Workwear, boca",
    "Street Style Photo": "Street style photo portrait, clear edge definition, unique and one-of-a-kind pieces, light brown and light amber, Fujifilm X-T4, Sony FE 85mm f/1.4 GM, —quality 2 —s 750 —v 5.2",
    "Space Astronaut": "In the style of Takashi Murakami, studio ghibli, bioshock infinite landscape, astronaut in space suit cartoon dynamic pose, fireworks, realistic photo, party, clouds, beautiful sky comets, cosmos, planets, sun",
    "Like a Pixar Film": "Pixar Film Style",
    "Paint Me Like Picasso": "A portrait painting of a person in the style of Picasso",
    "I'm a Super Hero": "Super Hero in the style of a Marvel character, shallow depth of field, vignette, highly detailed, high budget, bokeh, cinemascope, moody, epic, gorgeous, film grain, grainy",
    "Like Homer Simpson": "A yellow homer simpson, realistic portrait, symmetrical, highly detailed, digital painting, artstation, concept art, smooth, sharp focus, illustration, cinematic lighting",
    "Christmas Elf": "a Christmas Elf, Jolly, happy, bright, festive, lights, red santa hat, christmas, gifts",
    # "default" : "Type or Select prompt. Something like - pencil sketch of pizza and some cake",
    # "prompt-1": "a person in 8k resolution, photorealistic masterpiece by Aaron Horkey and Jeremy Mann, intricately detailed fluid gouache painting by Jean Baptiste, professional photography, natural lighting, volumetric lighting, maximalist, concept art, intricately detailed, complex, elegant, expansive cover",
    # "prompt-2": "anime style",
    # "prompt-3": "Portrait photo side profile, looking away, serious eyes, 50mm portrait photography, hard rim lighting photography–beta –ar 2:3 –beta –upbeta",
    # "prompt-4": "High Quality, Intricately Detailed, Hyper-Realistic Lawyer Portrait Photography, Volumetric Lighting, Full Character, 4k, In Workwear, boca",
    # "prompt-5": "Street style photo portrait, clear edge definition, unique and one-of-a-kind pieces, light brown and light amber, Fujifilm X-T4, Sony FE 85mm f/1.4 GM, —quality 2 —s 750 —v 5.2",
}

# Perform some crude state management
if "input_img" not in st.session_state:
    st.session_state.input_img = ''
if "gen_img" not in st.session_state:
    st.session_state.gen_img = ''


# start rendering the App
# if not check_password():
#     st.stop()

st.subheader("GenAI Application (beta)")

input_img = ''
input_slider = 60
image_seed = 0
style_preset='enhance'
uploaded_file = st.file_uploader("**Input Image**")
if uploaded_file:
    # remove rotation (when using smart-phone camera) and resize
    input_img = glib.remove_rotation(uploaded_file.getvalue())
    st.session_state.input_img = input_img
else:
    input_img = st.session_state.input_img

if input_img:
    st.image(input_img)
    input_slider = st.slider("Image strength", 1, 100, 60)
    with st.expander("What is Image Strength?"):
        st.write("""
        Image strength measures how good a text-to-image model is at turning words into pictures.
        
        If a model has an image strength closer to 0, the stable diffusion model will use less of your input image as the 'prompt' for the model
        
        The closer the Image Strength goes to 100, the stable diffusion will use more of your input image as the 'prompt' for the model. 
           
         
        """)

selection = st.selectbox("**Load Prompt**", some_prompts.keys())
prompt_text = st.text_area("**Input Text Prompt**", value = some_prompts[selection], 
                           height=50, key="prompt")

image_seed = st.slider("Seed", 0, 4294967295, 0)
with st.expander("What is an Image Generation Seed?"):
    st.write("""
    The Seed is a number from which Stable Diffusion generates noise. 
    
    You can reliably reproduce a generated image across multiple sessions if you input the same seed number as well as the same prompt and all of the same parameters you used to create the image in the first place
    
    A user can work off of someone else’s generated image by starting from the same seed, prompt and parameters as them.
    
    You can make minor tweaks to an image by slightly changing the prompt or parameters without significantly altering the images overall composition. 
    
    Some seeds have been identified by Stable Diffusion user communities as having a higher probability of producing images with specific color palettes or compositions. Knowing what those seeds are and using them therefore gives you a higher probability of getting an output image containing a characteristic you want.
       
     
    """)

style_preset = st.selectbox(
    'What Style Preset would you like to use?',
    ('enhance', 'anime', '3d-model', 'analog-film', 'cinematic', 'comic-book', 'digital-art', 'fantasy-art', 'isometric line-art', 'neon-punk', 'origami', 'photographic'))

process_button = st.button("Generate", type="primary")

gen_img = ''
st.subheader("Generated Image")
if process_button:
    with st.spinner("Drawing..."):
        image_bytes = input_img.getvalue() if input_img else None
        gen_img = glib.get_altered_image_from_model(prompt_content=prompt_text, image_bytes=image_bytes,
                                                    img_strength=input_slider, seed=image_seed, style_preset=style_preset)
        st.session_state.gen_img = gen_img
else:
    gen_img = st.session_state.gen_img
    
# generated output and download elements
if gen_img:
    st.image(gen_img)
    img_bytes = gen_img.getvalue()
    
    # placeholder for outputs
    outs = st.empty().container()
    checkbox = outs.checkbox("Upload for printing", value=True, key="checkbox")
    filename = outs.text_input("Image name:", key="filename")
    
    # Check if the filename already exists
    if filename and checkbox and glib.checkFileinS3(filename+".jpg"):
        filename = ''
        st.error("File already exists")
    
    outs.download_button(label="Download",
        data=img_bytes, 
        file_name=filename+".jpg",
        mime="image/jpg",
        disabled=not filename,
        on_click=s3_uploader, 
        args=[checkbox, filename+".jpg", img_bytes])