package lambda;

import java.util.Comparator;

public class Dog //implements Comparator<Dog>
{
	String name;
	String color;
	int weight;

	public Dog() {};
	public Dog(String n, String c, int w)
	{
		this.name = n;
		this.color = c;
		this.weight = w;
	}

/*	@Override
	public int compare(Dog dog1,Dog dog2)
	{
		return dog1.weight-dog2.weight;
	}*/
	@Override
	public String toString()
	{
		return getName() + ": color=" + getColor() + " weight=" + getWeight();
	}

	public String getName()
	{
		return name;
	}

	public String  getColor()
	{
		return color;
	}

	public int getWeight()
	{
		return weight;
	}
}