import React from 'react';
import './App.css';
import {Image, List, Menu, Segment, Sidebar} from 'semantic-ui-react'
import {withRouter} from "react-router-dom";


class Ingredient extends React.Component {
  render(){
    return <Menu.Item>{this.props.ingredient.original}</Menu.Item>
  }
}


class Ingredients extends React.Component {
  render(){
    let ingredients = []
    Object.keys(this.props.ingredients).forEach(cateogry => {
        this.props.ingredients[cateogry].forEach(ingredient => {
          ingredients.push(<Ingredient ingredient={ingredient} key={`ingredient_${ingredients.length}`}/>)
        })
    })


    return (<Sidebar
      as={Menu}
      icon='labeled'
      vertical
      visible={true}
      animation="slide out"
      width={"thin"}
    >
      <br/>
      <Menu.Header as={"h3"}>Ingredients</Menu.Header>
      {ingredients}
    </Sidebar>)
  }
}


class Instructions extends React.Component {
  render() {
    let i = 1;
    let steps = []
    Object.keys(this.props.instructions).forEach(category => {
      this.props.instructions[category].forEach(step => {
        steps.push(<List.Item key={"instruction_"+i} >

          <List.Content floated={"left"}>
            {i}) {step}
          </List.Content>
        </List.Item>)
        i += 1;
      })
    })
    return <List divided relaxed>
      <List.Header><h3>{this.props.title}</h3></List.Header>
      {steps}
      <List.Item>
        <List.Content>
          original recipe (<a href={this.props.url}>here</a>)
        </List.Content>
      </List.Item>
    </List>
  }
}


class Recipe extends React.Component {

  constructor(props) {
    super(props);
    this.state = {
      error: null,
      isLoaded: false,
      recipe: null
    };
  }

  componentDidMount() {
    this.loadRecipe()
  }

  loadRecipe(){
    let host = "https://recipes.oram.ca"
    if(window.location.hostname==="localhost")
      host = "http://localhost:5000"
    let pub_id = this.props.match.params.pub_id;
    fetch(`${host}/api/v0/recipe/${pub_id}`)
    .then(res => res.json())
    .then(recipe => {
      this.setState({
        isLoaded: true,
        recipe: recipe
      });
      console.log(recipe)
    })
  }

  render(){
    let ingredients = [];
    let instructions = [];
    let title = "";
    let src = ""
    let url = ""
    if (this.state.recipe !== null){
      ingredients = this.state.recipe.ingredients
      instructions = this.state.recipe.instructions
      title = this.state.recipe.title
      url = this.state.recipe.url
      if(this.state.recipe.images !== undefined){
        src = this.state.recipe.images.x512[0]
      }
    }

    return <>
      <Sidebar.Pushable as={Segment} style={{overflowY:"scroll"}}>
        <Ingredients ingredients={ingredients} />
        <Sidebar.Pusher>
          <Segment style={{marginRight:"150px"}} basic>
            <Image src={src} />
            <Instructions instructions={instructions} title={title} url={url} />
          </Segment>
        </Sidebar.Pusher>
      </Sidebar.Pushable>
    </>
  }
}

export default withRouter(Recipe);
